from models import FxTrade, RiskMetrics
from pricing import BlackScholesFxOptionPricer


class PricingService:
    def __init__(self, pricer=BlackScholesFxOptionPricer):
        self._pricer = pricer

    def price_trades(self, trades: list[FxTrade]) -> list[RiskMetrics]:
        return [self._pricer.price(t) for t in trades]
