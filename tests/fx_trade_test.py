import pytest
from pydantic import ValidationError

from models import FxTrade, OptionType


def test_fxtrade_valid_with_aliases():
    trade = FxTrade(
        TradeID="T00001",
        Underlying="EUR/USD",
        Notional=1_000_000,
        NotionalCurrency="USD",
        Spot=1.10,
        Strike=1.12,
        Vol=0.11,
        RateDomestic=0.02,
        RateForeign=0.01,
        Expiry=0.25,
        OptionType="Call"
    )

    assert trade.trade_id == "T00001"
    assert trade.underlying == "EUR/USD"
    assert trade.notional == 1_000_000
    assert trade.notional_currency == "USD"
    assert trade.spot_price == 1.1
    assert trade.strike_price == 1.12
    assert trade.vol == 0.11
    assert trade.rate_domestic == 0.02
    assert trade.rate_foreign == 0.01
    assert trade.expiry == 0.25
    assert trade.option_type is OptionType.CALL


def test_fxtrade_valid_with_field_names_populate_by_name():
    trade = FxTrade(
        trade_id="T002",
        underlying="GBP/USD",
        notional=500_000,
        notional_currency="GBP",
        spot_price=1.30,
        strike_price=1.25,
        vol=0.11,
        rate_domestic=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        option_type=OptionType.CALL
    )

    assert trade.trade_id == "T002"
    assert trade.underlying == "GBP/USD"
    assert trade.notional == 500_000
    assert trade.notional_currency == "GBP"
    assert trade.spot_price == 1.3
    assert trade.strike_price == 1.25
    assert trade.vol == 0.11
    assert trade.rate_domestic == 0.02
    assert trade.rate_foreign == 0.01
    assert trade.expiry == 0.25
    assert trade.option_type is OptionType.CALL


def test_negative_rates_allowed():
    trade = FxTrade(
        TradeID="T003",
        Underlying="EUR/CHF",
        Notional=1_000_000,
        NotionalCurrency="EUR",
        Spot=1.05,
        Strike=1.05,
        Vol=0.10,
        RateDomestic=-0.05,
        RateForeign=-0.02,
        Expiry=1.0,
        OptionType="Call"
    )

    assert trade.rate_domestic == -0.05
    assert trade.rate_foreign == -0.02


def test_underlying_is_uppercased():
    trade = FxTrade(
        TradeID="T004",
        Underlying="eur/usd",
        Notional=1_000_000,
        NotionalCurrency="EUR",
        Spot=1.10,
        Strike=1.10,
        Vol=0.12,
        RateDomestic=0.02,
        RateForeign=0.01,
        Expiry=0.25,
        OptionType="Call"
    )

    assert trade.underlying == "EUR/USD"


@pytest.mark.parametrize(
    "underlying",
    [
        "EURUSD",
        "EU/USD",
        "EURO/USD",
        "EUR/US",
        "EUR/USDD",
        "EUR/USD/GBP"
    ]
)
def test_invalid_underlying_rejected(underlying):
    with pytest.raises(ValidationError):
        FxTrade(
            TradeID="T005",
            Underlying=underlying,
            Notional=1_000_000,
            NotionalCurrency="EUR",
            Spot=1.10,
            Strike=1.10,
            Vol=0.12,
            RateDomestic=0.02,
            RateForeign=0.01,
            Expiry=0.25,
            OptionType="Call"
        )


@pytest.mark.parametrize("spot", [0, -1])
def test_negative_prices_rejected(spot):
    with pytest.raises(ValidationError):
        FxTrade(
            TradeID="T005",
            Underlying="EUR/USD",
            Notional=1_000_000,
            NotionalCurrency="EUR",
            Spot=spot,
            Strike=1.10,
            Vol=0.12,
            RateDomestic=0.02,
            RateForeign=0.01,
            Expiry=0.25,
            OptionType="Call"
        )


@pytest.mark.parametrize("option_type", ["call", "CALL", "CALL ", "Binary", "", "C"])
def test_invalid_option_type_rejected(option_type):
    with pytest.raises(ValidationError):
        FxTrade(
            TradeID="T008",
            Underlying="EUR/USD",
            Notional=1_000_000,
            NotionalCurrency="EUR",
            Spot=1.10,
            Strike=1.10,
            Vol=0.12,
            RateDomestic=0.02,
            RateForeign=0.01,
            Expiry=0.25,
            OptionType=option_type
        )


def test_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        FxTrade(
            TradeID="T010",
            Underlying="EUR/USD",
            Notional=1_000_000,
            NotionalCurrency="EUR",
            Spot=1.10,
            Strike=1.10,
            Vol=0.12,
            RateDomestic=0.02,
            RateForeign=0.01,
            Expiry=0.25,
            OptionType="Call",
            SthExtra="not allowed"
        )


def test_missing_required_field_rejected():
    # missing Notional
    with pytest.raises(ValidationError):
        FxTrade(
            TradeID="T011",
            Underlying="EUR/USD",
            NotionalCurrency="EUR",
            Spot=1.10,
            Strike=1.10,
            Vol=0.12,
            RateDomestic=0.02,
            RateForeign=0.01,
            Expiry=0.25,
            OptionType="Call"
        )
