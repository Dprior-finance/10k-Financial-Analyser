import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

_user_agent = os.getenv("SEC_USER_AGENT", "anonymous@example.com")
HEADERS = {"User-Agent": _user_agent}

_ticker_map: dict = {}

def _load_ticker_map() -> dict:
    """Download the SEC ticker list once and cache it in memory."""
    global _ticker_map
    if not _ticker_map:
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        _ticker_map = {item["ticker"]: str(item["cik_str"]).zfill(10) for item in data.values()}
    return _ticker_map


def get_cik(ticker: str) -> str:
    """Convert a ticker symbol to an SEC CIK number."""
    ticker = ticker.upper().replace(".", "-")
    ticker_map = _load_ticker_map()
    if ticker not in ticker_map:
        raise ValueError(f"Ticker '{ticker}' not found in SEC database.")
    return ticker_map[ticker]


def get_company_facts(cik: str) -> dict:
    """Pull all XBRL financial facts for a company."""
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def extract_annual(facts: dict, concept: str) -> pd.DataFrame:
    """Extract annual 10-K values for a given XBRL concept."""
    try:
        units = facts["facts"]["us-gaap"][concept]["units"]
        unit_key = list(units.keys())[0]
        records = units[unit_key]
    except KeyError:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df = df[df["form"] == "10-K"].copy()
    df = df[df["fp"] == "FY"].copy()

    # Keep only the largest value per year (full year, not partial)
    df["year"] = pd.to_datetime(df["end"]).dt.year
    df = df.sort_values("val", ascending=False)
    df = df.drop_duplicates(subset=["year"], keep="first")
    df = df.sort_values("year").reset_index(drop=True)

    return df[["year", "end", "val"]].rename(columns={"val": concept})


def extract_metric(facts: dict, concepts: list) -> pd.DataFrame:
    """
    Try all XBRL concept names against an already-fetched facts dict.
    Picks the concept with the most recent data, using row count as tiebreaker.
    """
    best_df = pd.DataFrame()
    best_concept = None
    best_latest_year = -1

    for concept in concepts:
        df = extract_annual(facts, concept)
        if df.empty:
            continue
        latest_year = df["year"].max()
        if latest_year > best_latest_year or (latest_year == best_latest_year and len(df) > len(best_df)):
            best_df = df
            best_concept = concept
            best_latest_year = latest_year

    if best_df.empty:
        raise ValueError(f"None of the concepts {concepts} found.")

    best_df = best_df.rename(columns={best_concept: "value"})
    best_df["concept"] = best_concept
    return best_df


def get_metric(ticker: str, concepts: list) -> pd.DataFrame:
    """Convenience wrapper — fetches facts then calls extract_metric."""
    cik = get_cik(ticker)
    facts = get_company_facts(cik)
    return extract_metric(facts, concepts)
