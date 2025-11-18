import argparse
import sys

from file_handler.excel_handler import ExcelHandler
from pricing.black_scholes_fx_option_pricer import BlackScholesFxOptionPricer
from service.pricing_service import PricingService
from service.aggregation_service import AggregationService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FX Options Portfolio Risk Aggregator")
    parser.add_argument("input", help="Input trades .xlsx file")
    parser.add_argument("output", help="Output .xlsx file")
    parser.add_argument(
        "--input_sheet",
        "-s",
        default="fx_trades",
        help="Name of the worksheet containing trades (default: fx_trades)",
    )
    return parser.parse_args()


def initialise_services(sheet_name: str) -> tuple[ExcelHandler, PricingService, AggregationService]:
    file_handler = ExcelHandler(sheet_name)
    pricing_service = PricingService(BlackScholesFxOptionPricer())
    aggregation_service = AggregationService()
    return file_handler, pricing_service, aggregation_service


def get_trades(file_handler, input_path: str):
    try:
        trades = file_handler.read_trades(input_path)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    return trades


def run(input_path: str, output_path: str, sheet_name: str) -> None:
    file_handler, pricing_service, aggregation_service = initialise_services(sheet_name)
    trades = get_trades(file_handler, input_path)
    metrics = pricing_service.price_trades(trades)
    summary = aggregation_service.aggregate(metrics)
    print(summary)
    file_handler.write_results(output_path, metrics, summary)


def main() -> None:
    args = parse_args()
    run(args.input, args.output, args.input_sheet)


if __name__ == "__main__":
    main()
