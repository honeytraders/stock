import logging
import os
import time
from typing import Optional

import sentry_sdk
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from broker_adapters.alpaca import AlpacaAdapter, AlpacaConfig
from core_contracts.license import LicenseService
from core_contracts.logging import setup_logging
from core_contracts.models import OrderType, Side
from core_contracts.state import SQLiteState

# Error Tracking
SENTRY_DSN = os.getenv("HTEQ__SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)

setup_logging()
logger = logging.getLogger("telegram_bot")

ALLOWED_CHAT_ID = os.getenv("HTEQ__TELEGRAM_CHAT_ID")

def get_state() -> SQLiteState:
    db_path = os.getenv("HTEQ__STATE_DB_PATH", "/app/data/state.db")
    return SQLiteState(db_path)

def get_broker() -> Optional[AlpacaAdapter]:
    key = os.getenv("HTEQ__ALPACA_KEY_ID")
    secret = os.getenv("HTEQ__ALPACA_SECRET_KEY")
    if not key or not secret:
        return None

    cfg = AlpacaConfig(
        api_key=key,
        secret_key=secret,
        base_url=os.getenv("HTEQ__ALPACA_BASE_URL", "https://paper-api.alpaca.markets"),
        data_url=os.getenv("HTEQ__ALPACA_DATA_URL", "https://data.alpaca.markets/v2"),
    )
    return AlpacaAdapter(cfg)

async def auth_check(update: Update) -> bool:
    if not update.effective_chat or str(update.effective_chat.id) != ALLOWED_CHAT_ID:
        if update.message:
            await update.message.reply_text("Unauthorized.")
        return False
    
    # License & Hardware Lock
    license_key = os.getenv("HTEQ__WHOP_LICENSE")
    if not LicenseService.validate(license_key):
        if update.message:
            await update.message.reply_text(
                "Verification failed. Ensure HTEQ__WHOP_LICENSE is set for this machine.\n"
                "Buy: https://whop.com/honeytrade"
            )
        return False
        
    return True

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await auth_check(update):
        return
    state = get_state()
    kbd = [["/status", "/positions"], ["/history", "/pause", "/resume"], ["/help"]]
    await update.message.reply_text(
        f"HTEQ Operator Plane\n"
        f"Mode: {os.getenv('HTEQ__MODE', 'paper')}\n"
        f"Active: {state.is_trading_enabled()}",
        reply_markup=ReplyKeyboardMarkup(kbd, one_time_keyboard=False),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await auth_check(update):
        return
    help_text = (
        "Command Help\n\n"
        "/status - Equity and buying power\n"
        "/positions - Open positions\n"
        "/history - Last 10 local trades\n"
        "/pause - Disable auto-trading\n"
        "/resume - Enable auto-trading\n"
        "/buy SYMBOL QTY - Manual buy\n"
        "/sell SYMBOL QTY - Manual sell"
    )
    await update.message.reply_text(help_text)


async def history_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await auth_check(update):
        return
    state = get_state()
    trades = state.get_trade_history(limit=10)
    if not trades:
        await update.message.reply_text("No trade history found.")
        return
    
    msg = "Recent Trades:\n" + "\n".join(
        [f"{t[5][:16]} | {t[1]} {t[2]} {t[3]} @ ${t[4]:,.2f}" for t in trades]
    )
    await update.message.reply_text(f"`{msg}`", parse_mode="MarkdownV2")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await auth_check(update):
        return
    broker = get_broker()
    state = get_state()
    if not broker:
        await update.message.reply_text("Missing broker config.")
        return

    try:
        acc = broker.get_account_status()
        msg = (
            f"Account Status ({os.getenv('HTEQ__MODE', 'paper')})\n"
            f"Equity: ${float(acc.get('equity', 0)):,.2f}\n"
            f"Buying Power: ${float(acc.get('buying_power', 0)):,.2f}\n"
            f"Trading: {state.is_trading_enabled()}"
        )
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"Status error: {e}")
        await update.message.reply_text("Error fetching status.")

async def positions_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await auth_check(update):
        return
    broker = get_broker()
    if not broker:
        return

    try:
        positions = broker.get_positions()
        if not positions:
            await update.message.reply_text("No positions.")
            return
        msg = "Open Positions:\n" + "\n".join(
            [f"{p.symbol}: {p.quantity} @ {p.average_entry_price}" for p in positions]
        )
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"Positions error: {e}")
        await update.message.reply_text("Error fetching positions.")

async def pause_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await auth_check(update):
        return
    get_state().set_trading_enabled(False)
    await update.message.reply_text("Trading disabled.")

async def resume_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await auth_check(update):
        return
    get_state().set_trading_enabled(True)
    await update.message.reply_text("Trading enabled.")

async def buy_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await auth_check(update):
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: /buy SYMBOL QTY")
        return

    symbol, qty = context.args[0].upper(), float(context.args[1])
    broker = get_broker()
    try:
        order = broker.submit_order(symbol, qty, Side.BUY, OrderType.MARKET, f"man-{int(time.time())}")
        await update.message.reply_text(f"Buy submitted: {order.id}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def sell_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await auth_check(update):
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: /sell SYMBOL QTY")
        return

    symbol, qty = context.args[0].upper(), float(context.args[1])
    broker = get_broker()
    try:
        order = broker.submit_order(symbol, qty, Side.SELL, OrderType.MARKET, f"man-s-{int(time.time())}")
        await update.message.reply_text(f"Sell submitted: {order.id}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

if __name__ == "__main__":
    token = os.getenv("HTEQ__TELEGRAM_BOT_TOKEN")
    if token:
        app = ApplicationBuilder().token(token).build()
        for cmd, handler in [
            ("start", start_cmd), ("help", help_cmd), ("status", status_cmd),
            ("positions", positions_cmd), ("history", history_cmd), ("pause", pause_cmd), 
            ("resume", resume_cmd), ("buy", buy_cmd), ("sell", sell_cmd)
        ]:
            app.add_handler(CommandHandler(cmd, handler))
        logger.info("Bot starting...")
        app.run_polling()
