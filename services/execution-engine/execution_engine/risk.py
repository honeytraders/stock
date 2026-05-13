from typing import Literal

from pydantic import BaseModel

from core_contracts.models import Side
from core_contracts.state import StatePort


class RiskConfig(BaseModel):
    max_positions: int = 5
    max_notional_per_trade_usd: float = 1000.0
    trading_enabled: bool = False
    acknowledge_live: str = ""
    mode: Literal["paper", "live"] = "paper"


class RiskModule:
    def __init__(self, config: RiskConfig, state: StatePort):
        self.config = config
        self.state = state

    def can_trade(
        self, symbol: str, side: Side, quantity: float, price: float, current_positions_count: int
    ) -> bool:
        # 1. Dynamic Kill switch (from DB)
        if not self.state.is_trading_enabled():
            return False

        # 2. Hard Kill switch (from ENV)
        if not self.config.trading_enabled:
            return False

        # 2. Live Guard: Must have explicit mode + ack string
        if self.config.mode == "live":
            if self.config.acknowledge_live != "I_UNDERSTAND_REAL_MONEY":
                return False

        # 3. Position limits
        if current_positions_count >= self.config.max_positions:
            return False

        # 4. Notional limits
        notional = quantity * price
        if notional > self.config.max_notional_per_trade_usd:
            return False

        return True
