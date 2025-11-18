import argparse
import sys

from file_handler.excel_handler import ExcelHandler
from pricing.black_scholes_fx_option_pricer import BlackScholesFxOptionPricer
from service.pricing_service import PricingService
from service.aggregation_service import AggregationService


APP_DESCRIPTION = "FX Options Portfolio Risk Aggregator"
ARG_INPUT = "input"
ARG_OUTPUT = "output"
ARG_INPUT_SHEET = "sheet"
ARG_INPUT_SHEET_SHORT = "-s"

DEFAULT_INPUT_SHEET = "fx_trades"
HELP_INPUT = "Input trades .xlsx file"
HELP_OUTPUT = "Output .xlsx file"
HELP_INPUT_SHEET = "Name of the worksheet containing trades (default: fx_trades)"

ERROR_PREFIX = "Error: "
EXIT_FAILURE = 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=APP_DESCRIPTION)
    parser.add_argument(ARG_INPUT, help=HELP_INPUT)
    parser.add_argument(ARG_OUTPUT, help=HELP_OUTPUT)
    parser.add_argument(
        f"--{ARG_INPUT_SHEET}",
        ARG_INPUT_SHEET_SHORT,
        default=DEFAULT_INPUT_SHEET,
        help=HELP_INPUT_SHEET,
    )
    return parser.parse_args()


def initialise_services(sheet_name: str) -> tuple[ExcelHandler, PricingService, AggregationService]:
    file_handler = ExcelHandler(sheet_name)
    pricing_service = PricingService(BlackScholesFxOptionPricer())
    aggregation_service = AggregationService()
    return file_handler, pricing_service, aggregation_service


def get_trades(file_handler: ExcelHandler, input_path: str):
    try:
        trades = file_handler.read_trades(input_path)
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"{ERROR_PREFIX}{e}", file=sys.stderr)
        sys.exit(EXIT_FAILURE)
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
