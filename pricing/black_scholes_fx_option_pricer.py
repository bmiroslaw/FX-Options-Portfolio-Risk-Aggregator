import math

from scipy import stats

from models import FxTrade, OptionType, RiskMetrics


class BlackScholesFxOptionPricer:
    """
    Black–Scholes FX options pricer based on the Garman–Kohlhagen formula.
    Assumptions:
      - trade notional is in the domestic currency
      - all trades are long
      - expiry is in years
      - vol is a decimal
    """

    @staticmethod
    def _d1(S: float, K: float, T: float, r_d: float, r_f: float, sigma: float) -> float:
        numerator = math.log(S / K) + (r_d - r_f + 0.5 * sigma ** 2) * T
        denominator = sigma * math.sqrt(T)
        return numerator / denominator

    @staticmethod
    def _d2(d1: float, sigma: float, T: float) -> float:
        return d1 - sigma * math.sqrt(T)

    @staticmethod
    def pv(trade: FxTrade) -> float:
        S, K, T, r_d, r_f, sigma = trade.to_pricing_inputs()
        d1 = BlackScholesFxOptionPricer()._d1(S, K, T, r_d, r_f, sigma)
        d2 = BlackScholesFxOptionPricer()._d2(d1, sigma, T)

        if trade.option_type == OptionType.CALL:
            price = (S * math.exp(-r_f*T) * stats.norm.cdf(d1) - K * math.exp(-r_d*T) * stats.norm.cdf(d2))
        else:
            price = (K * math.exp(-r_d*T) * stats.norm.cdf(-d2) - S * math.exp(-r_f*T) * stats.norm.cdf(-d1))
        return price * trade.notional

    @staticmethod
    def delta(trade: FxTrade) -> float:
        S, K, T, r_d, r_f, sigma = trade.to_pricing_inputs()
        d1 = BlackScholesFxOptionPricer()._d1(S, K, T, r_d, r_f, sigma)

        if trade.option_type == OptionType.CALL:
            delta = math.exp(-r_f * T) * stats.norm.cdf(d1)
        else:
            delta = -math.exp(-r_f * T) * stats.norm.cdf(-d1)
        return delta * trade.notional

    @staticmethod
    def _vega_raw(trade: FxTrade) -> float:
        S, K, T, r_d, r_f, sigma = trade.to_pricing_inputs()
        d1 = BlackScholesFxOptionPricer()._d1(S, K, T, r_d, r_f, sigma)
        vega = S * math.exp(-r_f * T) * stats.norm.pdf(d1) * math.sqrt(T)
        return vega * trade.notional

    @staticmethod
    def vega_1pct(trade: FxTrade) -> float:
        return BlackScholesFxOptionPricer()._vega_raw(trade) / 100.0

    @staticmethod
    def price(trade: FxTrade) -> RiskMetrics:
        pv = BlackScholesFxOptionPricer().pv(trade)
        delta = BlackScholesFxOptionPricer().delta(trade)
        vega = BlackScholesFxOptionPricer().vega_1pct(trade)
        return RiskMetrics(trade_id=trade.trade_id, pv=pv, delta=delta, vega=vega)
