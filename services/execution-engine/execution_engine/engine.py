import logging
import time
from typing import List, Protocol

import sentry_sdk
import os
from core_contracts.models import OrderType, Side
from core_contracts.ports import BrokerPort
from core_contracts.state import SQLiteState
from execution_engine.risk import RiskModule

# Staff Engineer: Sentry integration for engine
SENTRY_DSN = os.getenv("HTEQ__SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)

logger = logging.getLogger(__name__)


class Strategy(Protocol):
    def on_bar(self, symbol: str, bars: list) -> str:
        pass


class ExecutionEngine:
    def __init__(
        self, broker: BrokerPort, risk: RiskModule, watchlist: List[str], strategy: Strategy, state: SQLiteState
    ):
        self.broker = broker
        self.risk = risk
        self.watchlist = watchlist
        self.strategy = strategy
        self.state = state
        self.is_running = False

    def run_once(self):
        if not self.broker.is_market_open():
            logger.info("Market is closed. Skipping loop.")
            return

        positions = self.broker.get_positions()
        pos_map = {p.symbol: p for p in positions}

        for symbol in self.watchlist:
            try:
                bars = self.broker.get_bars(symbol, timeframe="1Min", limit=1)
                if not bars:
                    continue

                signal = self.strategy.on_bar(symbol, bars)
                current_price = bars[-1].close

                if signal == "BUY" and symbol not in pos_map:
                    if self.risk.can_trade(symbol, Side.BUY, 1, current_price, len(positions)):
                        logger.info(f"Signal: BUY {symbol} @ {current_price}")
                        self.broker.submit_order(
                            symbol, 1, Side.BUY, OrderType.MARKET, f"hteq-{int(time.time())}"
                        )
                        self.state.log_trade(symbol, "BUY", 1, current_price)

                elif signal == "SELL" and symbol in pos_map:
                    logger.info(f"Signal: SELL {symbol} @ {current_price}")
                    qty = pos_map[symbol].quantity
                    self.broker.submit_order(
                        symbol,
                        qty,
                        Side.SELL,
                        OrderType.MARKET,
                        f"hteq-exit-{int(time.time())}",
                    )
                    self.state.log_trade(symbol, "SELL", qty, current_price)

            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                sentry_sdk.capture_exception(e)

    def start(self, interval: int = 60):
        self.is_running = True
        while self.is_running:
            self.run_once()
            time.sleep(interval)

    def stop(self):
        self.is_running = False
