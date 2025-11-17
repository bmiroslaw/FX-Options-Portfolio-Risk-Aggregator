from models import PortfolioSummary
from models import RiskMetrics


def test_from_metrics_sums_all_fields():
    metrics = [
        RiskMetrics(trade_id="T1", pv=100.0, delta=10.0, vega=1.0),
        RiskMetrics(trade_id="T2", pv=100.0, delta=10.0, vega=1),
    ]

    summary = PortfolioSummary.from_metrics(metrics)

    assert summary.total_pv == 200.0
    assert summary.total_delta == 20.0
    assert summary.total_vega == 2
    assert summary.num_trades == 2 
