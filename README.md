# FX Options Portfolio Risk Aggregator

Python application for pricing and aggregating FX options using the **Garman–Kohlhagen Black–Scholes model**.  
Tested with Python **3.11.1**.
---

## Overview

This app reads a portfolio of FX option trades from an Excel file, validates them using **Pydantic**, computes risk metrics using a Black–Scholes Garman–Kohlhagen pricer, and outputs both:

- a trade-level result table  
- a portfolio summary (total PV, Delta, Vega)

### Main Components
- **Excel I/O** – Loading trades & writing results (`ExcelHandler`)
- **Pydantic Models** – Validation of data
- **Pricing Engine** – Black–Scholes FX pricer (`BlackScholesFxOptionPricer`)
- **Services Layer** – Pricing & aggregation
- **CLI Tool** – Command-line execution

---

## The Model

The application uses the **Garman–Kohlhagen** extension of Black–Scholes for FX options.

Given spot `S`, strike `K`, domestic and foreign interest rates (`r_d`, `r_f`), volatility `σ`, and expiry `T` in years, the pricer computes:

- **PV** (present value)
- **Delta** (spot sensitivity)
- **Vega (1%)** (price change for a 1% change in volatility)

Assumptions:
* Trade notional is in the domestic currency
* All trades are long
* Expiry is in years
* Vol is a decimal 
All outputs are scaled by notional.

---

## Installation

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Usage

### Command Line

```bash
python3 main.py trades.xlsx results.xlsx
```

Specify a custom worksheet name for the input .xlsx file (default is **fx_trades**):

```bash
python3 main.py trades.xlsx results.xlsx --input_sheet Sheet1
```

The app prints a portfolio summary and writes:

- Trade-level PV / Delta / Vega  
- Portfolio totals  

to the output Excel file.

---

## Tests

```bash
python -m pytest -q
```

Run an individual suite:

```bash
python -m pytest tests/black_scholes_fx_option_pricer_test.py -q
```

---

## Input Format

Excel input sheet must contain the following columns:

| Column            | Meaning                      |
|-------------------|------------------------------|
| TradeID           | Unique trade identifier      |
| Underlying        | Format: `EUR/USD`            |
| Notional          | Notional amount              |
| NotionalCurrency  | Currency (e.g. USD)          |
| Spot              | Spot FX rate                 |
| Strike            | Strike FX rate               |
| Vol               | Volatility (decimal)         |
| RateDomestic      | Domestic interest rate       |
| RateForeign       | Foreign interest rate        |
| Expiry            | Time to expiry in years      |
| OptionType        | `Call` or `Put`              |

Any missing or invalid fields will raise validation errors.

---

## Project Structure

```text
FX-Options-Portfolio-Risk-Aggregator/
├── file_handler/
│   └── excel_handler.py
├── models/
│   ├── fx_trade.py
│   ├── portfolio_summary.py
│   ├── risk_metrics.py
├── pricing/
│   └── black_scholes_fx_option_pricer.py
├── service/
│   ├── pricing_service.py
│   └── aggregation_service.py
├── main.py
├── tests/
├── trades.xlsx
└── README.md
```
