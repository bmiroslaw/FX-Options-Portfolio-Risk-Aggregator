from enum import Enum
from pydantic import BaseModel, Field, PositiveFloat, field_validator


class OptionType(str, Enum):
    CALL = 'Call'
    PUT = 'Put'


class FxTrade(BaseModel):
    trade_id: str = Field(alias="TradeID")
    underlying: str = Field(alias="Underlying")
    notional: PositiveFloat = Field(alias="Notional")
    notional_currency: str = Field(alias="NotionalCurrency")
    spot_price: PositiveFloat = Field(alias="Spot")
    strike_price: PositiveFloat = Field(alias="Strike")
    vol: PositiveFloat = Field(alias="Vol")
    rate_domestic: float = Field(alias="RateDomestic")
    rate_foreign: float = Field(alias="RateForeign")
    expiry: PositiveFloat = Field(alias="Expiry")
    option_type: OptionType = Field(alias="OptionType")

    @field_validator("underlying")
    @classmethod
    def validate_underlying(cls, v):
        parts = v.split("/")
        if len(parts) != 2 or any(len(p) != 3 for p in parts):
            raise ValueError("Underlying must be formatted like 'EUR/USD'")
        return v.upper()

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "frozen": True
    }

    def to_pricing_inputs(self) -> tuple[float, float, float, float, float, float]:
        return (
            self.spot_price,
            self.strike_price,
            self.expiry,
            self.rate_domestic,
            self.rate_foreign,
            self.vol,
        )
