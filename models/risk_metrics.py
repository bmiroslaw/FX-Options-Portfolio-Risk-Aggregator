from pydantic import BaseModel


class RiskMetrics(BaseModel):
    """
    Risk measures for an individual FX option trade.
    """
    trade_id: str
    pv: float
    delta: float
    vega: float

    model_config = {
        "frozen": True
    }
