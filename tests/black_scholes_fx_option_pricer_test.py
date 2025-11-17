import pytest

from models import FxTrade, RiskMetrics
from pricing.black_scholes_fx_option_pricer import BlackScholesFxOptionPricer
from tests.utils import QuantLibPricer


@pytest.fixture
def call_trade() -> FxTrade:
    return FxTrade(
        TradeID="T000001",
        Underlying="EUR/USD",
        Notional=1_000_000,
        NotionalCurrency="USD",
        Spot=1.10,
        Strike=1.12,
        Vol=0.11,
        RateDomestic=0.02,
        RateForeign=0.01,
        Expiry=1,
        OptionType="Call"
    )


@pytest.fixture
def put_trade() -> FxTrade:
    return FxTrade(
        TradeID="T000002",
        Underlying="EUR/USD",
        Notional=500_000,
        NotionalCurrency="USD",
        Spot=1.10,
        Strike=1.10,
        Vol=0.12,
        RateDomestic=0.02,
        RateForeign=0.01,
        Expiry=1,
        OptionType="Put"
    )


@pytest.mark.parametrize("trade_fixture_name", ["call_trade", "put_trade"])
def test_pv_delta_vega_matches_quantlib(trade_fixture_name: str, request: pytest.FixtureRequest):
    trade: FxTrade = request.getfixturevalue(trade_fixture_name)

    result = BlackScholesFxOptionPricer().price(trade)
    assert isinstance(result, RiskMetrics)
    assert result.trade_id == trade.trade_id

    ql_pv, ql_delta, ql_vega_1pct = QuantLibPricer()._ql_pv_delta_vega_1pct(trade)

    assert [result.pv, result.delta, result.vega] == pytest.approx([ql_pv, ql_delta, ql_vega_1pct], rel=1e-12)
