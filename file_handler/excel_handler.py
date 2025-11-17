from models import FxTrade, PortfolioSummary, RiskMetrics
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

    def write_results(
            self,
            path: str,
            trades: list[FxTrade],
            metrics: list[RiskMetrics],
            summary: PortfolioSummary,
    ) -> None:
        trades_df = pd.DataFrame([t.model_dump(by_alias=True) for t in trades])
        metrics_df = pd.DataFrame([m.model_dump() for m in metrics])
        metrics_df = metrics_df.rename(columns={"trade_id": "TradeID"})
        merged = trades_df.merge(metrics_df, on="TradeID")
        summary_df = pd.DataFrame([summary.model_dump()])

        with pd.ExcelWriter(path) as writer:
            merged.to_excel(writer, sheet_name=self.trade_results_sheet, index=False)
            summary_df.to_excel(writer, sheet_name=self.portfolio_summary_sheet, index=False)
