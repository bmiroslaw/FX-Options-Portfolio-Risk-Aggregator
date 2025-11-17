import pytest

from models import FxTrade, RiskMetrics
from service import PricingService
from tests.utils import QuantLibPricer


@pytest.fixture
def trades() -> list[FxTrade]:
    return [
        FxTrade(
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
        ),
        FxTrade(
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
    ]


def test_pricing_service_prices_all_trades(trades: list[FxTrade]):
    ps = PricingService()
    metrics = ps.price_trades(trades)

    assert len(metrics) == 2
    assert [m.trade_id for m in metrics] == ["T000001", "T000002"]
    assert all(isinstance(m, RiskMetrics) for m in metrics)
    assert all(
        m.pv == pytest.approx(QuantLibPricer()._ql_pv_delta_vega_1pct(t)[0], rel=1e-12)
        for m, t in zip(metrics, trades)
    )
