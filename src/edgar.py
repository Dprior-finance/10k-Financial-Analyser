import requests
import pandas as pd

HEADERS = {"User-Agent": "your-email@example.com"}

def get_cik(ticker: str) -> str:
    """Convert a ticker symbol to an SEC CIK number."""
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    
    ticker = ticker.upper()
    for item in data.values():
        if item["ticker"] == ticker:
            return str(item["cik_str"]).zfill(10)
    
    raise ValueError(f"Ticker '{ticker}' not found in SEC database.")


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


def get_metric(ticker: str, concepts: list) -> pd.DataFrame:
    """
    Try multiple XBRL concept names until one works.
    Returns a clean annual series for the first concept found.
    """
    cik = get_cik(ticker)
    facts = get_company_facts(cik)
    
    for concept in concepts:
        df = extract_annual(facts, concept)
        if not df.empty:
            df = df.rename(columns={concept: "value"})
            df["concept"] = concept
            return df
    
    raise ValueError(f"None of the concepts {concepts} found for {ticker}.")