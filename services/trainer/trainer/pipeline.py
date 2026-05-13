import argparse
import hashlib
import json
import os
from datetime import datetime
from typing import List

import lightgbm as lgb
import pandas as pd
import yfinance as yf
from trainer.labeling import build_binary_next_bar_up_targets


class Trainer:
    def __init__(self, output_dir: str = "model_bundle"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def download_data(
        self, symbols: List[str], start: str, end: str, interval: str = "1h"
    ) -> pd.DataFrame:
        dfs = []
        for symbol in symbols:
            df = yf.download(symbol, start=start, end=end, interval=interval, progress=False)
            if df.empty:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.columns = [c.lower() for c in df.columns]

            df = df.reset_index()
            # Ensure price column exists
            df["symbol"] = symbol
            dfs.append(df)

        if not dfs:
            return pd.DataFrame()

        full_df = pd.concat(dfs)
        # Find timestamp column (usually 'Date' or 'Datetime' -> 'date' or 'datetime')
        ts_cols = [c for c in ["date", "datetime"] if c in full_df.columns]
        if not ts_cols:
            raise ValueError(
                f"No timestamp column ('date' or 'datetime') found. Columns: {full_df.columns.tolist()}"
            )

        ts_col = ts_cols[0]
        full_df = full_df.sort_values(["symbol", ts_col])
        return full_df

    def train(self, data: pd.DataFrame, target_col: str = "close"):
        if data.empty:
            return

        ts_cols = [c for c in ["date", "datetime"] if c in data.columns]
        if not ts_cols:
            raise ValueError(
                f"No timestamp column ('date' or 'datetime') found. Columns: {data.columns.tolist()}"
            )
        ts_col = ts_cols[0]

        data = data.sort_values(["symbol", ts_col])

        # Use shared labeling function
        data["target"] = build_binary_next_bar_up_targets(data, "symbol", target_col)
        data = data.dropna(subset=["target"])

        features_list = ["open", "high", "low", "close", "volume"]
        missing = [f for f in features_list if f not in data.columns]
        if missing:
            raise ValueError(f"Missing feature columns: {missing}")

        features = data[features_list].values
        labels = data["target"].values

        train_data = lgb.Dataset(features, label=labels)
        model = lgb.train({"objective": "binary", "verbose": -1}, train_data, num_boost_round=10)

        model_filename = "model.txt"
        model_path = os.path.join(self.output_dir, model_filename)
        model.save_model(model_path)

        self._export_bundle(model_path, model_filename, features_list)

    def _export_bundle(self, model_path: str, model_filename: str, features: List[str]):
        with open(model_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        manifest = {
            "version": "0.1.0",
            "created_at": datetime.now().isoformat(),
            "features": features,
            "model_file": model_filename,
            "sha256": file_hash,
        }

        with open(os.path.join(self.output_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", default="AAPL,TSLA", help="Comma-separated symbols")
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default="2024-01-31")
    parser.add_argument("--interval", default="1h")
    parser.add_argument("--output", default="model_bundle")
    args = parser.parse_args()

    trainer = Trainer(args.output)
    data = trainer.download_data(args.symbols.split(","), args.start, args.end, args.interval)
    trainer.train(data)


if __name__ == "__main__":
    main()
