from models import FxTrade, OptionType
import QuantLib as ql


class QuantLibPricer:
    @staticmethod
    def _ql_pv_delta_vega_1pct(trade: FxTrade) -> tuple[float, float, float]:
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
