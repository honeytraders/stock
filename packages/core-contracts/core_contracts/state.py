import sqlite3
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class StatePort(ABC):
    @abstractmethod
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        pass

    @abstractmethod
    def set_setting(self, key: str, value: str):
        pass

    @abstractmethod
    def is_trading_enabled(self) -> bool:
        pass

    @abstractmethod
    def set_trading_enabled(self, enabled: bool):
        pass


class SQLiteState(StatePort):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS trades (id TEXT PRIMARY KEY, symbol TEXT, side TEXT, quantity REAL, price REAL, timestamp TEXT)"
            )
            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES ('trading_enabled', 'false')"
            )

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else default

    def set_setting(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value)
            )

    def is_trading_enabled(self) -> bool:
        return self.get_setting("trading_enabled", "false").lower() == "true"

    def set_trading_enabled(self, enabled: bool):
        self.set_setting("trading_enabled", "true" if enabled else "false")

    def log_trade(self, symbol: str, side: str, quantity: float, price: float):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO trades (id, symbol, side, quantity, price, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (f"{symbol}-{int(time.time())}", symbol, side, quantity, price, datetime.now().isoformat())
            )

    def get_trade_history(self, limit: int = 10) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?", (limit,))
            return cur.fetchall()
