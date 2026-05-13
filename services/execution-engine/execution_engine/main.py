import logging
import os
import sys

from broker_adapters.alpaca import AlpacaAdapter, AlpacaConfig
from core_contracts.bundle import verify_bundle
from core_contracts.logging import setup_logging
from core_contracts.state import SQLiteState
from execution_engine.engine import ExecutionEngine
from execution_engine.risk import RiskConfig, RiskModule
from execution_engine.strategies import LGBMStrategy, NoOpStrategy, SmokeStrategy


def main():
    setup_logging()
    logger = logging.getLogger("execution_engine.main")

    # Bundle Policy: HTEQ__REQUIRE_MODEL_BUNDLE (default false)
    # If folder empty/missing: warn and continue if not required.
    require_bundle = os.getenv("HTEQ__REQUIRE_MODEL_BUNDLE", "false").lower() == "true"
    bundle_path = os.getenv("HTEQ__MODEL_BUNDLE_PATH", "./model_bundle")
    manifest_exists = os.path.exists(os.path.join(bundle_path, "manifest.json"))

    if manifest_exists:
        if not verify_bundle(bundle_path):
            logger.error("Model bundle verification failed. Exiting.")
            sys.exit(1)
        logger.info("Model bundle loaded and verified.")
    elif require_bundle:
        logger.error(
            f"HTEQ__REQUIRE_MODEL_BUNDLE is true but manifest missing at {bundle_path}. Exiting."
        )
        sys.exit(1)
    else:
        logger.warning(
            f"No model bundle manifest found at {bundle_path}. Engine will run with Paper/Smoke/NoOp strategy only."
        )

    # Config from ENV
    alpaca_cfg = AlpacaConfig(
        api_key=os.getenv("HTEQ__ALPACA_KEY_ID", ""),
        secret_key=os.getenv("HTEQ__ALPACA_SECRET_KEY", ""),
        base_url=os.getenv("HTEQ__ALPACA_BASE_URL", "https://paper-api.alpaca.markets"),
        data_url=os.getenv("HTEQ__ALPACA_DATA_URL", "https://data.alpaca.markets/v2"),
    )

    risk_cfg = RiskConfig(
        max_positions=int(os.getenv("HTEQ__RISK_MAX_POSITIONS", "5")),
        max_notional_per_trade_usd=float(os.getenv("HTEQ__RISK_MAX_NOTIONAL_USD", "1000")),
        trading_enabled=os.getenv("HTEQ__TRADING_ENABLED", "false").lower() == "true",
        acknowledge_live=os.getenv("HTEQ__ACK_LIVE", ""),
        mode=os.getenv("HTEQ__MODE", "paper"),
    )

    broker = AlpacaAdapter(alpaca_cfg)
    risk = RiskModule(risk_cfg)

    # Strategy Selection
    strat_type = os.getenv("HTEQ__STRATEGY", "noop").lower()
    if strat_type == "smoke" and risk_cfg.mode == "paper":
        logger.info("Running with SmokeStrategy (PAPER ONLY)")
        strategy = SmokeStrategy()
    elif strat_type == "lgbm":
        if manifest_exists:
            logger.info(f"Running with LGBMStrategy using bundle at {bundle_path}")
            strategy = LGBMStrategy(bundle_path)
        else:
            logger.error("LGBM strategy selected but no model bundle found. Falling back to NoOp.")
            strategy = NoOpStrategy()
    else:
        # Default to NoOp
        if strat_type != "noop":
            logger.warning(
                f"Strategy {strat_type} not implemented or unsafe for current mode. Falling back to NoOpStrategy."
            )
        strategy = NoOpStrategy()

    watchlist = os.getenv("HTEQ__WATCHLIST", "AAPL,TSLA,MSFT").split(",")

    engine = ExecutionEngine(broker, risk, watchlist, strategy, state)

    try:
        engine.start(interval=60)
    except KeyboardInterrupt:
        engine.stop()
    except Exception as e:
        logger.critical(f"Unhandled exception in engine: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
Unhandled exception in engine: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
