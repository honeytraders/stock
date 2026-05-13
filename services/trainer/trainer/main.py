import logging
import os
import time
from datetime import datetime, timedelta

from core_contracts.logging import setup_logging
from trainer.pipeline import Trainer

setup_logging()
logger = logging.getLogger("trainer.main")


def run_training_cycle():
    symbols = os.getenv("HTEQ__WATCHLIST", "AAPL,TSLA,MSFT").split(",")
    output_dir = os.getenv("HTEQ__MODEL_BUNDLE_PATH", "./model_bundle")
    
    # Training window: last 60 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    trainer = Trainer(output_dir)
    
    logger.info(f"Starting training cycle for {symbols} from {start_date.date()} to {end_date.date()}")
    try:
        data = trainer.download_data(
            symbols, 
            start=start_date.strftime("%Y-%m-%d"), 
            end=end_date.strftime("%Y-%m-%d"), 
            interval="1h"
        )
        if data.empty:
            logger.warning("No data downloaded. Skipping training.")
            return
            
        trainer.train(data)
        logger.info("Training cycle completed successfully.")
    except Exception as e:
        logger.error(f"Training cycle failed: {e}")


def main():
    mode = os.getenv("HTEQ__TRAINER_MODE", "once").lower()
    interval_hours = int(os.getenv("HTEQ__TRAINER_INTERVAL_HOURS", "24"))

    if mode == "once":
        run_training_cycle()
    elif mode == "service":
        logger.info(f"Trainer running in service mode. Interval: {interval_hours} hours.")
        while True:
            run_training_cycle()
            logger.info(f"Sleeping for {interval_hours} hours...")
            time.sleep(interval_hours * 3600)
    else:
        logger.error(f"Unknown HTEQ__TRAINER_MODE: {mode}")


if __name__ == "__main__":
    main()
