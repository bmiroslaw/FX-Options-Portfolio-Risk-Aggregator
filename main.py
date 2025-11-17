# main.py
import argparse

from file_handler.excel_handler import ExcelHandler
from pricing.black_scholes_fx_option_pricer import BlackScholesFxOptionPricer
from service.pricing_service import PricingService
from service.aggregation_service import AggregationService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    excel = ExcelHandler()
    pricer = BlackScholesFxOptionPricer()
    pricing_service = PricingService(pricer)
    aggregation_service = AggregationService()

    trades = excel.read_trades(args.input)
    metrics = pricing_service.price_trades(trades)
    summary = aggregation_service.aggregate(metrics)

    excel.write_results(args.output, trades, metrics, summary)


if __name__ == "__main__":
    main()
