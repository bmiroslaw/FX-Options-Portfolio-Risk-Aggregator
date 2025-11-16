from models.fx_trade import FxTrade
import pandas as pd


class ExcelHandler:
    def __init__(
            self,
            input_sheet: str = "fx_trades",
            trade_results_sheet: str = "TradeLevelResults",
            portfolio_summary_sheet: str = "PortfolioSummary",
    ) -> None:
        self.input_sheet = input_sheet
        self.trade_results_sheet = trade_results_sheet
        self.portfolio_summary_sheet = portfolio_summary_sheet

    def read_trades(self, path: str) -> list[FxTrade]:
        df = pd.read_excel(path, sheet_name=self.input_sheet)
        trades: list[FxTrade] = []
        errors: list[tuple[int, Exception]] = []

        for row_num, (_, row) in enumerate(df.iterrows(), start=1):
            try:
                trade = FxTrade.model_validate(row.to_dict())
                trades.append(trade)
            except Exception as exc:
                errors.append((row_num, exc))

        if errors:
            msg = "Failed to parse some trade rows:\n" + "\n".join(f"Row {i}: {e}" for i, e in errors)
            raise ValueError(msg)

        return trades
