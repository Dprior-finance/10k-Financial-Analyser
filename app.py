import streamlit as st
import pandas as pd
from src.ratios import build_analysis
from src.charts import (
    margin_trends,
    revenue_growth_chart,
    revenue_chart,
    fcf_chart,
    comps_table
)

st.set_page_config(
    page_title="10K Financial Analyser",
    page_icon="📊",
    layout="wide"
)

st.title("📊 10K Financial Analyser")
st.markdown("Comparable company analysis powered by SEC EDGAR public data.")
st.divider()

# Sidebar
st.sidebar.header("Configure Analysis")

ticker_input = st.sidebar.text_input(
    "Enter tickers (comma separated)",
    value="MSFT, AAPL, GOOGL",
    help="Use SEC ticker symbols e.g. MSFT, AAPL, GOOGL"
)

run_button = st.sidebar.button("Run Analysis", type="primary")

st.sidebar.divider()
st.sidebar.markdown("**Data Source**")
st.sidebar.markdown("SEC EDGAR XBRL API")
st.sidebar.markdown("Annual 10-K filings only")
st.sidebar.markdown("[View on GitHub](https://github.com/Dprior-finance/10k-Financial-Analyser)")

# Run analysis and store in session state
if run_button:
    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
    if tickers:
        with st.spinner(f"Pulling 10-K data for {', '.join(tickers)}..."):
            try:
                df = build_analysis(tickers)
                st.session_state["df"] = df
                st.session_state["tickers"] = tickers
                st.success(f"Data loaded for {', '.join(tickers)}")
            except Exception as e:
                st.error(f"Error: {e}")

# Display results if data exists in session state
if "df" in st.session_state:
    df = st.session_state["df"]
    tickers = st.session_state["tickers"]

    available_years = sorted(df["year"].dropna().unique(), reverse=True)
    selected_year = st.selectbox(
        "Select year for comps table",
        options=available_years,
        index=0
    )

    st.divider()

    st.subheader("Comparable Company Analysis")
    fig_table = comps_table(df, selected_year)
    st.plotly_chart(fig_table, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue")
        fig_rev = revenue_chart(df, tickers)
        st.plotly_chart(fig_rev, use_container_width=True)

    with col2:
        st.subheader("Revenue Growth")
        fig_growth = revenue_growth_chart(df, tickers)
        st.plotly_chart(fig_growth, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Margin Trends")
        fig_margins = margin_trends(df, tickers)
        st.plotly_chart(fig_margins, use_container_width=True)

    with col4:
        st.subheader("Free Cash Flow")
        fig_fcf = fcf_chart(df, tickers)
        st.plotly_chart(fig_fcf, use_container_width=True)

    st.divider()

    with st.expander("View raw data"):
        st.dataframe(df.sort_values(["ticker", "year"]))

else:
    st.markdown("### How to use")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**1. Enter tickers**")
        st.markdown("Type comma separated ticker symbols in the sidebar e.g. MSFT, AAPL, GOOGL")

    with col2:
        st.markdown("**2. Run analysis**")
        st.markdown("Click Run Analysis. Data is pulled live from SEC EDGAR 10-K filings.")

    with col3:
        st.markdown("**3. Explore**")
        st.markdown("View the comps table, margin trends, revenue growth and free cash flow charts.")

    st.divider()
    st.markdown("Built with SEC EDGAR public data · No API key required · Annual 10-K filings only")