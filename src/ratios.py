import numpy as np
import pandas as pd
from src.model import build_model, build_comps


def add_margins(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate gross, operating and net profit margins."""
    df = df.copy()
    if "gross_profit" in df.columns:
        df["gross_margin"] = df["gross_profit"] / df["revenue"]
    else:
        df["gross_margin"] = np.nan
    df["operating_margin"] = df["operating_income"] / df["revenue"]
    df["net_margin"] = df["net_income"] / df["revenue"]
    return df


def add_growth_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate year over year growth rates per ticker."""
    df = df.copy()
    df = df.sort_values(["ticker", "year"])
    df["revenue_growth"] = df.groupby("ticker")["revenue"].pct_change()
    df["net_income_growth"] = df.groupby("ticker")["net_income"].pct_change()
    df["operating_cf_growth"] = df.groupby("ticker")["operating_cashflow"].pct_change()
    return df


def add_fcf(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate free cash flow."""
    df = df.copy()
    if "capex" in df.columns:
        df["fcf"] = df["operating_cashflow"] - df["capex"]
        df["fcf_margin"] = df["fcf"] / df["revenue"]
    else:
        df["fcf"] = np.nan
        df["fcf_margin"] = np.nan
    return df


def add_multiples(df: pd.DataFrame, price_data: dict = None) -> pd.DataFrame:
    """
    Add valuation multiples.
    price_data = {"MSFT": 420.0, "AAPL": 195.0} etc.
    If no price data provided, skips market multiples.
    """
    df = df.copy()

    # EV/Revenue and EV/EBITDA require market data
    # We will add these in the dashboard when user inputs prices
    # For now calculate what we can from financials only

    df["debt_to_equity"] = df["total_debt"] / df["total_equity"]
    df["return_on_equity"] = df["net_income"] / df["total_equity"]
    df["return_on_assets"] = df["net_income"] / df["total_assets"]
    df["asset_turnover"] = df["revenue"] / df["total_assets"]

    return df


def build_analysis(tickers: list) -> pd.DataFrame:
    """
    Full pipeline — pull data, calculate all ratios.
    Returns a clean DataFrame ready for the dashboard.
    """
    print(f"Building analysis for: {tickers}")
    df = build_comps(tickers)
    df = add_margins(df)
    df = add_growth_rates(df)
    df = add_fcf(df)
    df = add_multiples(df)
    return df
