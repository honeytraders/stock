from core_contracts.models import Side
from execution_engine.risk import RiskConfig, RiskModule


def test_risk_live_gate_requires_ack():
    # Live mode but wrong/empty ack
    cfg = RiskConfig(mode="live", acknowledge_live="WRONG", trading_enabled=True)
    risk = RiskModule(cfg)
    assert risk.can_trade("AAPL", Side.BUY, 1, 150.0, 0) is False


def test_risk_live_gate_passes_with_ack():
    cfg = RiskConfig(mode="live", acknowledge_live="I_UNDERSTAND_REAL_MONEY", trading_enabled=True)
    risk = RiskModule(cfg)
    assert risk.can_trade("AAPL", Side.BUY, 1, 150.0, 0) is True


def test_risk_kill_switch():
    cfg = RiskConfig(mode="paper", trading_enabled=False)
    risk = RiskModule(cfg)
    assert risk.can_trade("AAPL", Side.BUY, 1, 150.0, 0) is False
