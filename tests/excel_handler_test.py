import pytest
import pandas as pd

from file_handler import ExcelHandler
from models import FxTrade, OptionType


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
