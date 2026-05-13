import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    NEW = "new"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


class Bar(BaseModel):
    timestamp: datetime.datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str


class SignalType(str, Enum):
    FLAT = "flat"
    ENTER_LONG = "enter_long"
    EXIT = "exit"
    REDUCE = "reduce"


class Signal(BaseModel):
    symbol: str
    signal_type: SignalType
    strength: float = 1.0
    timestamp: datetime.datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Order(BaseModel):
    id: Optional[str] = None
    client_order_id: str
    symbol: str
    side: Side
    order_type: OrderType
    quantity: float
    limit_price: Optional[float] = None
    status: OrderStatus = OrderStatus.NEW
    filled_quantity: float = 0.0
    average_fill_price: Optional[float] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class Position(BaseModel):
    symbol: str
    quantity: float
    average_entry_price: float
    current_price: Optional[float] = None
    unrealized_pl: float = 0.0
