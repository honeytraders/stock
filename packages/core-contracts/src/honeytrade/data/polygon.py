import aiohttp
from datetime import datetime
from typing import Dict, List
from honeytrade.config import config
from .provider import MarketDataProvider

class PolygonDataProvider(MarketDataProvider):
    async def get_historical_data(self, symbol: str, start: datetime, end: datetime, timeframe: str = '1d') -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            url = f'https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start.date()}/{end.date()}'
            params = {'apiKey': config.POLYGON_API_KEY}
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                return data.get('results', [])

    async def get_real_time_price(self, symbol: str) -> float:
        # Polygon real-time endpoint (simplified)
        return 150.0  # placeholder
