import pytest
import QuantLib as ql

from models import FxTrade, OptionType, RiskMetrics
from pricing.black_scholes_fx_option_pricer import BlackScholesFxOptionPricer


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
        OptionType="Call",
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
        OptionType="Put",
    )


def _ql_pv_delta_vega_1pct(trade: FxTrade) -> tuple[float, float, float]:
    """
    Price the given FxTrade with QuantLib
    https://quantlib-python-docs.readthedocs.io/en/latest/pricing_engines.html#option-pricing-engines
    """

    S, K, T, r_d, r_f, sigma = trade.to_pricing_inputs()

    # Evaluation date and maturity
    today = ql.Date.todaysDate()
    days_to_maturity = int(T * 365 + 0.5)
    maturity = today + days_to_maturity

    riskFreeTS = ql.YieldTermStructureHandle(ql.FlatForward(today, r_d, ql.Actual365Fixed()))
    dividendTS = ql.YieldTermStructureHandle(ql.FlatForward(today, r_f, ql.Actual365Fixed()))
    volatility = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(today, ql.NullCalendar(), sigma, ql.Actual365Fixed()))
    initialValue = ql.QuoteHandle(ql.SimpleQuote(S))
    process = ql.BlackScholesMertonProcess(initialValue, dividendTS, riskFreeTS, volatility)

    if trade.option_type == OptionType.CALL:
        ql_type = ql.Option.Call
    else:
        ql_type = ql.Option.Put

    payoff = ql.PlainVanillaPayoff(ql_type, K)
    exercise = ql.EuropeanExercise(maturity)
    option = ql.VanillaOption(payoff, exercise)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process))

    pv_per_unit = option.NPV()
    delta_per_unit = option.delta()
    vega_per_unit_1pct = option.vega() / 100
    pv = pv_per_unit * trade.notional
    delta = delta_per_unit * trade.notional
    vega_1pct = vega_per_unit_1pct * trade.notional
    return pv, delta, vega_1pct


def test_pv_delta_vega_call_matches_quantlib(call_trade: FxTrade):
    result = BlackScholesFxOptionPricer().price(call_trade)
    assert isinstance(result, RiskMetrics)
    assert result.trade_id == call_trade.trade_id

    ql_pv, ql_delta, ql_vega_1pct = _ql_pv_delta_vega_1pct(call_trade)

    assert result.pv == pytest.approx(ql_pv, rel=1e-12)
    assert result.delta == pytest.approx(ql_delta, rel=1e-12)
    assert result.vega == pytest.approx(ql_vega_1pct, rel=1e-12)


def test_pv_delta_vega_put_matches_quantlib(put_trade: FxTrade):
    result = BlackScholesFxOptionPricer().price(put_trade)
    assert isinstance(result, RiskMetrics)
    assert result.trade_id == put_trade.trade_id

    ql_pv, ql_delta, ql_vega_1pct = _ql_pv_delta_vega_1pct(put_trade)

    assert result.pv == pytest.approx(ql_pv, rel=1e-12)
    assert result.delta == pytest.approx(ql_delta, rel=1e-12)
    assert result.vega == pytest.approx(ql_vega_1pct, rel=1e-12)
