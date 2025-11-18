from models import RiskMetrics, PortfolioSummary


class AggregationService:
    """
    # Aggregates Trades' RiskMetrics into a single PortfolioSummary.
    """
    @staticmethod
    def aggregate(metrics: list[RiskMetrics]) -> PortfolioSummary:
        return PortfolioSummary.from_metrics(metrics)
