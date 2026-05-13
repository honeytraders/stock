from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

class MarketDataProvider(ABC):
    @abstractmethod
    def get_historical_data(self, symbol: str, timeframe: str, start_date: datetime, end_date: datetime):
        pass

    @abstractmethod
    def get_latest_price(self, symbol: str) -> float:
        pass
