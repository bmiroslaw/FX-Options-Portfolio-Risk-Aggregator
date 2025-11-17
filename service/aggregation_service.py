from models import RiskMetrics, PortfolioSummary


class AggregationService:

    @staticmethod
    def aggregate(metrics: list[RiskMetrics]) -> PortfolioSummary:
        return PortfolioSummary.from_metrics(metrics)
