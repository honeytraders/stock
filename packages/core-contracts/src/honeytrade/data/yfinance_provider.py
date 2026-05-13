import yfinance as yf
from datetime import datetime
from typing import Dict, List
from .provider import MarketDataProvider

class YFinanceDataProvider(MarketDataProvider):
    async def get_historical_data(self, symbol: str, start: datetime, end: datetime, timeframe: str = '1d') -> List[Dict]:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, interval=timeframe)
        return df.reset_index().to_dict('records')

    async def get_real_time_price(self, symbol: str) -> float:
        ticker = yf.Ticker(symbol)
        return ticker.info.get('regularMarketPrice', 0.0)
