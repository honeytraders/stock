import datetime
import logging
from typing import List

import httpx
from pydantic import BaseModel

from core_contracts.models import Bar, Order, OrderStatus, OrderType, Position, Side
from core_contracts.ports import BrokerPort

logger = logging.getLogger(__name__)


class AlpacaConfig(BaseModel):
    api_key: str
    secret_key: str
    base_url: str = "https://paper-api.alpaca.markets"
    data_url: str = "https://data.alpaca.markets/v2"


class AlpacaAdapter(BrokerPort):
    def __init__(self, config: AlpacaConfig):
        self.config = config
        self.headers = {"APCA-API-KEY-ID": config.api_key, "APCA-API-SECRET-KEY": config.secret_key}
        self.client = httpx.Client(base_url=self.config.base_url, headers=self.headers)
        self.data_client = httpx.Client(base_url=self.config.data_url, headers=self.headers)

    def get_account_status(self) -> dict:
        resp = self.client.get("/v2/account")
        resp.raise_for_status()
        return resp.json()

    def get_positions(self) -> List[Position]:
        resp = self.client.get("/v2/positions")
        resp.raise_for_status()
        return [
            Position(
                symbol=p["symbol"],
                quantity=float(p["qty"]),
                average_entry_price=float(p["avg_entry_price"]),
                current_price=float(p["current_price"]),
                unrealized_pl=float(p["unrealized_pl"]),
            )
            for p in resp.json()
        ]

    def submit_order(
        self, symbol: str, quantity: float, side: Side, order_type: OrderType, client_order_id: str
    ) -> Order:
        payload = {
            "symbol": symbol,
            "qty": str(quantity),
            "side": side.value,
            "type": order_type.value,
            "time_in_force": "gtc",
            "client_order_id": client_order_id,
        }
        resp = self.client.post("/v2/orders", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return Order(
            id=data["id"],
            client_order_id=data["client_order_id"],
            symbol=data["symbol"],
            side=side,
            order_type=order_type,
            quantity=float(data["qty"]),
            status=OrderStatus.SUBMITTED,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )

    def get_bars(self, symbol: str, timeframe: str = "1Min", limit: int = 100) -> List[Bar]:
        params = {"timeframe": timeframe, "limit": limit}
        # Data API v2 endpoint for stocks
        resp = self.data_client.get(f"/stocks/{symbol}/bars", params=params)
        resp.raise_for_status()
        # Data API returns { "bars": { "SYMBOL": [...] } }
        bars_data = resp.json().get("bars", {}).get(symbol, [])
        return [
            Bar(
                timestamp=datetime.datetime.fromisoformat(b["t"].replace("Z", "+00:00")),
                open=b["o"],
                high=b["h"],
                low=b["l"],
                close=b["c"],
                volume=b["v"],
                symbol=symbol,
            )
            for b in bars_data
        ]

    def is_market_open(self) -> bool:
        resp = self.client.get("/v2/clock")
        resp.raise_for_status()
        return resp.json().get("is_open", False)
