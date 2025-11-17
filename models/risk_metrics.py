from pydantic import BaseModel


class RiskMetrics(BaseModel):
    trade_id: str
    pv: float
    delta: float
    vega: float

    model_config = {
        "frozen": True
    }
