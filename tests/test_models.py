from datetime import datetime, timezone

from core_contracts.models import Bar, Order, OrderStatus, OrderType, Side, Signal, SignalType


def test_bar_model():
    bar = Bar(
        timestamp=datetime.now(timezone.utc),
        open=150.0,
        high=155.0,
        low=149.0,
        close=152.0,
        volume=1000,
        symbol="AAPL",
    )
    assert bar.symbol == "AAPL"
    assert bar.close == 152.0


def test_signal_model():
    signal = Signal(
        symbol="TSLA", signal_type=SignalType.ENTER_LONG, timestamp=datetime.now(timezone.utc)
    )
    assert signal.symbol == "TSLA"
    assert signal.signal_type == SignalType.ENTER_LONG


def test_order_model():
    order = Order(
        client_order_id="test-1",
        symbol="MSFT",
        side=Side.BUY,
        order_type=OrderType.MARKET,
        quantity=10,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    assert order.status == OrderStatus.NEW
    assert order.quantity == 10
