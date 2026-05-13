import json
import os
from typing import List

import lightgbm as lgb
import pandas as pd

from core_contracts.models import Bar
from execution_engine.engine import Strategy


class NoOpStrategy(Strategy):
    def on_bar(self, symbol: str, bars: List[Bar]) -> str:
        return "FLAT"


class SmokeStrategy(Strategy):
    def on_bar(self, symbol: str, bars: List[Bar]) -> str:
        # Simple signal to verify integration: Buy if last close > 0
        if bars and bars[-1].close > 0:
            return "BUY"
        return "FLAT"


class LGBMStrategy(Strategy):
    def __init__(self, bundle_path: str):
        self.bundle_path = bundle_path
        self.manifest_path = os.path.join(bundle_path, "manifest.json")
        self._load_bundle()
        self.last_manifest_mtime = os.path.getmtime(self.manifest_path)

    def _load_bundle(self) -> None:
        with open(self.manifest_path, "r") as f:
            self.manifest = json.load(f)
        model_path = os.path.join(self.bundle_path, self.manifest["model_file"])
        self.model = lgb.Booster(model_file=model_path)
        self.features = self.manifest["features"]
        logger.info(f"Loaded model bundle created at {self.manifest.get('created_at')}")

    def _check_reload(self) -> None:
        try:
            current_mtime = os.path.getmtime(self.manifest_path)
            if current_mtime > self.last_manifest_mtime:
                logger.info("New model bundle detected. Reloading...")
                self._load_bundle()
                self.last_manifest_mtime = current_mtime
        except Exception as e:
            logger.error(f"Error checking for model reload: {e}")

    def on_bar(self, symbol: str, bars: List[Bar]) -> str:
        self._check_reload()
        if not bars:
            return "FLAT"

        # Prepare features from the last bar
        # In a real scenario, we might want to calculate indicators here
        last_bar = bars[-1]
        data = {
            "open": [last_bar.open],
            "high": [last_bar.high],
            "low": [last_bar.low],
            "close": [last_bar.close],
            "volume": [last_bar.volume],
        }
        df = pd.DataFrame(data)

        # Ensure features match what the model expects
        # Note: If the model uses technical indicators, we'd calculate them here
        X = df[self.features].values
        prediction = self.model.predict(X)[0]

        # Simple thresholding
        if prediction > 0.6:  # High confidence buy
            return "BUY"
        elif prediction < 0.4:  # Low confidence / sell signal
            return "SELL"
        return "FLAT"
