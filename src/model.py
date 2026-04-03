import pandas as pd
from src.edgar import get_metric

# XBRL concept mappings - multiple fallbacks per metric
CONCEPTS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
        "Revenues",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "SalesRevenueGoodsNet",
    ],
    "gross_profit": [
        "GrossProfit",
    ],
    "operating_income": [
        "OperatingIncomeLoss",
    ],
    "net_income": [
        "NetIncomeLoss",
        "ProfitLoss",
    ],
    "ebitda_proxy": [
        "OperatingIncomeLoss",  # We'll add D&A separately later
    ],
    "total_assets": [
        "Assets",
    ],
    "total_debt": [
        "LongTermDebt",
        "LongTermDebtAndCapitalLeaseObligations",
        "DebtAndCapitalLeaseObligations",
    ],
    "total_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "operating_cashflow": [
        "NetCashProvidedByUsedInOperatingActivities",
    ],
    "capex": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
    ],
}


def build_model(ticker: str) -> pd.DataFrame:
    """
    Pull all key metrics for a ticker and return a clean
    annual DataFrame with one row per year.
    """
    ticker = ticker.upper()
    model = None

    for metric_name, concepts in CONCEPTS.items():
        try:
            df = get_metric(ticker, concepts)
            df = df[["year", "value"]].rename(columns={"value": metric_name})

            if model is None:
                model = df
            else:
                model = pd.merge(model, df, on="year", how="outer")

        except ValueError:
            print(f"  Warning: {metric_name} not found for {ticker}")
            continue

    if model is None:
        raise ValueError(f"No data found for {ticker}")

    model = model.sort_values("year").reset_index(drop=True)
    model.insert(0, "ticker", ticker)

    return model


def build_comps(tickers: list) -> pd.DataFrame:
    """Build a combined model for multiple tickers."""
    frames = []
    for ticker in tickers:
        print(f"Pulling data for {ticker}...")
        try:
            df = build_model(ticker)
            frames.append(df)
        except ValueError as e:
            print(f"  Skipped {ticker}: {e}")
            continue

    if not frames:
        raise ValueError("No data retrieved for any ticker.")

    return pd.concat(frames, ignore_index=True)