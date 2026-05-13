import datetime
from unittest.mock import MagicMock

import pytest

from core_contracts.models import Bar, Side
from execution_engine.engine import ExecutionEngine
from execution_engine.risk import RiskConfig, RiskModule


@pytest.fixture
def mock_broker():
    broker = MagicMock()
    broker.is_market_open.return_value = True
    broker.get_positions.return_value = []
    broker.get_bars.return_value = [
        Bar(
            timestamp=datetime.datetime.now(),
            open=100,
            high=101,
            low=99,
            close=100,
            volume=1000,
            symbol="AAPL",
        )
    ]
    return broker


@pytest.fixture
def mock_strategy():
    strategy = MagicMock()
    strategy.on_bar.return_value = "BUY"
    return strategy


def test_engine_executes_buy(mock_broker, mock_strategy):
    risk = RiskModule(RiskConfig(trading_enabled=True))
    engine = ExecutionEngine(mock_broker, risk, ["AAPL"], mock_strategy)
    engine.run_once()
    assert mock_broker.submit_order.called
    args = mock_broker.submit_order.call_args[0]
    assert args[0] == "AAPL"
    assert args[2] == Side.BUY


def test_engine_respects_kill_switch(mock_broker, mock_strategy):
    risk = RiskModule(RiskConfig(trading_enabled=False))
    engine = ExecutionEngine(mock_broker, risk, ["AAPL"], mock_strategy)
    engine.run_once()
    assert not mock_broker.submit_order.called
