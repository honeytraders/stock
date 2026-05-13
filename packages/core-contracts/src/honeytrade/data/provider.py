from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from honeytrade.config import config

class MarketDataProvider(ABC):
    @abstractmethod
    async def get_historical_data(self, symbol: str, start: datetime, end: datetime, timeframe: str = '1d') -> List[Dict]:
        pass

    @abstractmethod
    async def get_real_time_price(self, symbol: str) -> float:
        pass

class DataProviderFactory:
    @staticmethod
    def get_provider() -> MarketDataProvider:
        if config.POLYGON_API_KEY and config.POLYGON_API_KEY != 'YOUR_POLYGON_KEY':
            from .polygon import PolygonDataProvider
            return PolygonDataProvider()
        else:
            from .yfinance_provider import YFinanceDataProvider
            return YFinanceDataProvider()
