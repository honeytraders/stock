from abc import ABC, abstractmethod
from typing import List

from core_contracts.models import Bar, Order, OrderType, Position, Side


class BrokerPort(ABC):
    @abstractmethod
    def get_account_status(self) -> dict:
        """Returns account equity, buying power, etc."""
        pass

    @abstractmethod
    def get_positions(self) -> List[Position]:
        pass

    @abstractmethod
    def submit_order(
        self, symbol: str, quantity: float, side: Side, order_type: OrderType, client_order_id: str
    ) -> Order:
        pass

    @abstractmethod
    def get_bars(self, symbol: str, timeframe: str, limit: int) -> List[Bar]:
        pass

    @abstractmethod
    def is_market_open(self) -> bool:
        pass
