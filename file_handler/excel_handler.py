import pandas as pd

from models import FxTrade, PortfolioSummary, RiskMetrics

DEFAULT_INPUT_SHEET = "fx_trades"
DEFAULT_TRADE_RESULTS_SHEET = "TradeLevelResults"
DEFAULT_PORTFOLIO_SUMMARY_SHEET = "PortfolioSummary"

TRADE_ID_FIELD = "trade_id"
TRADE_ID_COLUMN = "TradeID"

ERROR_FILE_NOT_FOUND = "Input file not found: {}"
ERROR_READ_SHEET = "Failed to read sheet '{}' from '{}': {}"
ERROR_READ_GENERIC = "Failed to read trades from '{}': {}"
ERROR_PARSE_ROWS_HEADER = "Failed to parse some trade rows:\n"
ERROR_PARSE_ROW_LINE = "Row {}: {}"


class ExcelHandler:
    def __init__(
            self,
            input_sheet: str = DEFAULT_INPUT_SHEET,
            trade_results_sheet: str = DEFAULT_TRADE_RESULTS_SHEET,
            portfolio_summary_sheet: str = DEFAULT_PORTFOLIO_SUMMARY_SHEET,
    ) -> None:
        self.input_sheet = input_sheet
        self.trade_results_sheet = trade_results_sheet
        self.portfolio_summary_sheet = portfolio_summary_sheet

    def read_trades(self, path: str) -> list[FxTrade]:
        df = self._load_dataframe(path)
        return self._parse_trades(df)

    def write_results(
        self,
        path: str,
        metrics: list[RiskMetrics],
        summary: PortfolioSummary,
    ) -> None:
        metrics_df = pd.DataFrame([m.model_dump() for m in metrics])
        metrics_df = metrics_df.rename(columns={TRADE_ID_FIELD: TRADE_ID_COLUMN})
        summary_df = pd.DataFrame([summary.model_dump()])

        with pd.ExcelWriter(path) as writer:
            metrics_df.to_excel(writer, sheet_name=self.trade_results_sheet, index=False)
            summary_df.to_excel(writer, sheet_name=self.portfolio_summary_sheet, index=False)

    def _load_dataframe(self, path: str) -> pd.DataFrame:
        try:
            return pd.read_excel(path, sheet_name=self.input_sheet)
        except FileNotFoundError as e:
            raise FileNotFoundError(ERROR_FILE_NOT_FOUND.format(path)) from e
        except ValueError as e:
            raise ValueError(ERROR_READ_SHEET.format(self.input_sheet, path, e)) from e
        except Exception as e:
            raise RuntimeError(ERROR_READ_GENERIC.format(path, e)) from e

    def _parse_trades(self, df: pd.DataFrame) -> list[FxTrade]:
        trades: list[FxTrade] = []
        errors: list[tuple[int, Exception]] = []

        for row_num, (_, row) in enumerate(df.iterrows(), start=1):
            try:
                trade = FxTrade.model_validate(row.to_dict())
                trades.append(trade)
            except Exception as exc:
                errors.append((row_num, exc))

        if errors:
            msg = ERROR_PARSE_ROWS_HEADER + "\n".join(ERROR_PARSE_ROW_LINE.format(i, e) for i, e in errors)
            raise ValueError(msg)

        return trades
