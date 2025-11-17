from pydantic import BaseModel

from models import RiskMetrics


class PortfolioSummary(BaseModel):
    total_pv: float
    total_delta: float
    total_vega: float
    num_trades: int

    model_config = {
        "frozen": True
    }

    @classmethod
    def from_metrics(cls, metrics: list[RiskMetrics]) -> "PortfolioSummary":
        total_pv = sum(m.pv for m in metrics)
        total_delta = sum(m.delta for m in metrics)
        total_vega = sum(m.vega for m in metrics)
        num_trades = len(metrics)
        return cls(total_pv=total_pv, total_delta=total_delta, total_vega=total_vega, num_trades=num_trades)
