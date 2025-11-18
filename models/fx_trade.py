from enum import Enum
from pydantic import BaseModel, Field, PositiveFloat, field_validator

ALIAS_TRADE_ID = "TradeID"
ALIAS_UNDERLYING = "Underlying"
ALIAS_NOTIONAL = "Notional"
ALIAS_NOTIONAL_CCY = "NotionalCurrency"
ALIAS_SPOT = "Spot"
ALIAS_STRIKE = "Strike"
ALIAS_VOL = "Vol"
ALIAS_RATE_DOMESTIC = "RateDomestic"
ALIAS_RATE_FOREIGN = "RateForeign"
ALIAS_EXPIRY = "Expiry"
ALIAS_OPTION_TYPE = "OptionType"

UNDERLYING_SEPARATOR = "/"
UNDERLYING_LEG_LENGTH = 3
UNDERLYING_ERROR_MSG = "Underlying must be formatted like 'EUR/USD'"


class OptionType(str, Enum):
    CALL = "Call"
    PUT = "Put"


class FxTrade(BaseModel):
    """
    Trade model for a single FX option trade.
    """
    trade_id: str = Field(alias=ALIAS_TRADE_ID)
    underlying: str = Field(alias=ALIAS_UNDERLYING)
    notional: PositiveFloat = Field(alias=ALIAS_NOTIONAL)
    notional_currency: str = Field(alias=ALIAS_NOTIONAL_CCY)
    spot_price: PositiveFloat = Field(alias=ALIAS_SPOT)
    strike_price: PositiveFloat = Field(alias=ALIAS_STRIKE)
    vol: PositiveFloat = Field(alias=ALIAS_VOL)
    rate_domestic: float = Field(alias=ALIAS_RATE_DOMESTIC)
    rate_foreign: float = Field(alias=ALIAS_RATE_FOREIGN)
    expiry: PositiveFloat = Field(alias=ALIAS_EXPIRY)
    option_type: OptionType = Field(alias=ALIAS_OPTION_TYPE)

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
        "frozen": True,
    }

    @field_validator("underlying")
    @classmethod
    def validate_underlying(cls, v: str) -> str:
        parts = v.split(UNDERLYING_SEPARATOR)
        if len(parts) != 2 or any(len(p) != UNDERLYING_LEG_LENGTH for p in parts):
            raise ValueError(UNDERLYING_ERROR_MSG)
        return v.upper()

    def to_pricing_inputs(self) -> tuple[float, float, float, float, float, float]:
        return (
            self.spot_price,
            self.strike_price,
            self.expiry,
            self.rate_domestic,
            self.rate_foreign,
            self.vol,
        )
