from pydantic import BaseModel

from models import RiskMetrics


class PortfolioSummary(BaseModel):
    """
    Aggregated portfolio-level risk metrics.
    """
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

    def __str__(self) -> str:
        return (
            "PortfolioSummary:\n"
            f" Trades:      {self.num_trades}\n"
            f" Total PV:    {self.total_pv:,.3f}\n"
            f" Total Delta: {self.total_delta:,.3f}\n"
            f" Total Vega:  {self.total_vega:,.3f}"
        )

    def __repr__(self) -> str:
        return str(self)
