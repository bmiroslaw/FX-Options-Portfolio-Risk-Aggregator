import pytest
import pandas as pd

from file_handler import ExcelHandler
from models import FxTrade, OptionType, RiskMetrics, PortfolioSummary


def create_dummy_trades_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "TradeID": "T000001",
                "Underlying": "EUR/USD",
                "Notional": 1_000_000,
                "NotionalCurrency": "USD",
                "Spot": 1.10,
                "Strike": 1.12,
                "Vol": 0.11,
                "RateDomestic": 0.02,
                "RateForeign": 0.01,
                "Expiry": 0.25,
                "OptionType": "Call",
            },
            {
                "TradeID": "T000002",
                "Underlying": "GBP/USD",
                "Notional": 500_000,
                "NotionalCurrency": "USD",
                "Spot": 1.30,
                "Strike": 1.28,
                "Vol": 0.13,
                "RateDomestic": 0.015,
                "RateForeign": 0.01,
                "Expiry": 0.50,
                "OptionType": "Put",
            },
        ]
    )


def test_read_trades_correct_path(tmp_path):
    df = create_dummy_trades_df()
    path = tmp_path / "fx_trades.xlsx"
    df.to_excel(path, sheet_name="fx_trades", index=False)

    io = ExcelHandler()
    trades = io.read_trades(str(path))

    assert len(trades) == 2
    assert all(isinstance(t, FxTrade) for t in trades)

    trade = trades[0]
    assert trade.trade_id == "T000001"
    assert trade.underlying == "EUR/USD"
    assert trade.notional == 1_000_000
    assert trade.notional_currency == "USD"
    assert trade.spot_price == 1.1
    assert trade.strike_price == 1.12
    assert trade.vol == 0.11
    assert trade.rate_domestic == 0.02
    assert trade.rate_foreign == 0.01
    assert trade.expiry == 0.25
    assert trade.option_type is OptionType.CALL


def test_read_trades_invalid_underlying(tmp_path):
    df = create_dummy_trades_df()
    df.loc[0, "Underlying"] = "EURUSD"

    path = tmp_path / "trades_invalid_underlying.xlsx"
    df.to_excel(path, sheet_name="Sheet1", index=False)
    io = ExcelHandler(input_sheet="Sheet1")

    with pytest.raises(ValueError) as e:
        io.read_trades(str(path))

    msg = str(e.value)
    assert "Failed to parse some trade rows" in msg
    assert "Underlying must be formatted like 'EUR/USD'" in msg


def test_read_trades_extra_column(tmp_path):
    df = create_dummy_trades_df()
    df["extra"] = 123

    path = tmp_path / "trades_extra_col.xlsx"
    df.to_excel(path, sheet_name="fx_trades", index=False)
    io = ExcelHandler(input_sheet="fx_trades")

    with pytest.raises(ValueError) as e:
        io.read_trades(str(path))

    msg = str(e.value)
    assert "Failed to parse some trade rows" in msg


def test_write_results_creates_expected_sheets_and_columns(tmp_path):
    trades = [
        FxTrade(
            TradeID="T000001",
            Underlying="EUR/USD",
            Notional=1_000_000,
            NotionalCurrency="USD",
            Spot=1.10,
            Strike=1.12,
            Vol=0.11,
            RateDomestic=0.02,
            RateForeign=0.01,
            Expiry=1,
            OptionType="Call",
        ),
        FxTrade(
            TradeID="T000002",
            Underlying="GBP/USD",
            Notional=500_000,
            NotionalCurrency="USD",
            Spot=1.30,
            Strike=1.28,
            Vol=0.13,
            RateDomestic=0.015,
            RateForeign=0.01,
            Expiry=1,
            OptionType="Put",
        ),
    ]

    metrics = [
        RiskMetrics(trade_id="T000001", pv=1000.0, delta=500.0, vega=200.0),
        RiskMetrics(trade_id="T000002", pv=2000.0, delta=600.0, vega=300.0),
    ]

    summary = PortfolioSummary(
        total_pv=3000.0,
        total_delta=1100.0,
        total_vega=500.0,
        num_trades=2,
    )

    path = tmp_path / "results.xlsx"
    io = ExcelHandler()
    io.write_results(str(path), trades, metrics, summary)

    with pd.ExcelFile(path) as xls:
        sheet_names = set(xls.sheet_names)
        assert "TradeLevelResults" in sheet_names
        assert "PortfolioSummary" in sheet_names

        trade_results_df = pd.read_excel(xls, sheet_name="TradeLevelResults")
        summary_df = pd.read_excel(xls, sheet_name="PortfolioSummary")

    expected_trade_cols = {
        "TradeID",
        "Underlying",
        "Notional",
        "NotionalCurrency",
        "Spot",
        "Strike",
        "Vol",
        "RateDomestic",
        "RateForeign",
        "Expiry",
        "OptionType",
        "pv",
        "delta",
        "vega",
    }
    assert expected_trade_cols.issubset(set(trade_results_df.columns))
    assert summary_df.loc[0, "total_pv"] == pytest.approx(3000.0)
    assert summary_df.loc[0, "total_delta"] == pytest.approx(1100.0)
    assert summary_df.loc[0, "total_vega"] == pytest.approx(500.0)
    assert summary_df.loc[0, "num_trades"] == 2
