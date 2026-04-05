import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


COLOURS = px.colors.qualitative.Set2


def margin_trends(df: pd.DataFrame, tickers: list) -> go.Figure:
    """Line chart showing gross, operating and net margins over time."""
    fig = go.Figure()

    for i, ticker in enumerate(tickers):
        company = df[df["ticker"] == ticker]
        colour = COLOURS[i % len(COLOURS)]

        fig.add_trace(go.Scatter(
            x=company["year"],
            y=company["gross_margin"],
            name=f"{ticker} Gross Margin",
            line=dict(color=colour, dash="solid"),
            mode="lines+markers"
        ))

        fig.add_trace(go.Scatter(
            x=company["year"],
            y=company["operating_margin"],
            name=f"{ticker} Operating Margin",
            line=dict(color=colour, dash="dash"),
            mode="lines+markers"
        ))

        fig.add_trace(go.Scatter(
            x=company["year"],
            y=company["net_margin"],
            name=f"{ticker} Net Margin",
            line=dict(color=colour, dash="dot"),
            mode="lines+markers"
        ))

    fig.update_layout(
        title="Margin Trends",
        xaxis_title="Year",
        yaxis_title="Margin",
        yaxis_tickformat=".0%",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=-0.4),
        height=500
    )

    return fig


def revenue_growth_chart(df: pd.DataFrame, tickers: list) -> go.Figure:
    """Bar chart comparing revenue growth rates."""
    fig = go.Figure()

    for i, ticker in enumerate(tickers):
        company = df[df["ticker"] == ticker].dropna(subset=["revenue_growth"])
        colour = COLOURS[i % len(COLOURS)]

        fig.add_trace(go.Bar(
            x=company["year"],
            y=company["revenue_growth"],
            name=ticker,
            marker_color=colour
        ))

    fig.update_layout(
        title="Revenue Growth (YoY)",
        xaxis_title="Year",
        yaxis_title="Growth Rate",
        yaxis_tickformat=".0%",
        barmode="group",
        hovermode="x unified",
        height=500
    )

    return fig


def revenue_chart(df: pd.DataFrame, tickers: list) -> go.Figure:
    """Bar chart showing absolute revenue per company."""
    fig = go.Figure()

    for i, ticker in enumerate(tickers):
        company = df[df["ticker"] == ticker]
        colour = COLOURS[i % len(COLOURS)]

        fig.add_trace(go.Bar(
            x=company["year"],
            y=company["revenue"] / 1e9,
            name=ticker,
            marker_color=colour
        ))

    fig.update_layout(
        title="Annual Revenue",
        xaxis_title="Year",
        yaxis_title="Revenue (USD Billions)",
        barmode="group",
        hovermode="x unified",
        height=500
    )

    return fig


def fcf_chart(df: pd.DataFrame, tickers: list) -> go.Figure:
    """Line chart showing free cash flow over time."""
    fig = go.Figure()

    for i, ticker in enumerate(tickers):
        company = df[df["ticker"] == ticker]
        colour = COLOURS[i % len(COLOURS)]

        fig.add_trace(go.Scatter(
            x=company["year"],
            y=company["fcf"] / 1e9,
            name=ticker,
            line=dict(color=colour),
            mode="lines+markers"
        ))

    fig.update_layout(
        title="Free Cash Flow",
        xaxis_title="Year",
        yaxis_title="FCF (USD Billions)",
        hovermode="x unified",
        height=500
    )

    return fig


def comps_table(df: pd.DataFrame, year: int) -> go.Figure:
    """Summary comps table for a given year."""
    filtered = df[df["year"] == year].copy()

    def fmt_pct(series):
        return series.apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")

    def fmt_bn(series):
        return series.apply(lambda x: round(x, 1) if pd.notna(x) else "—")

    filtered["revenue_bn"] = fmt_bn(filtered["revenue"] / 1e9)
    filtered["gross_margin_pct"] = fmt_pct(filtered["gross_margin"] * 100)
    filtered["operating_margin_pct"] = fmt_pct(filtered["operating_margin"] * 100)
    filtered["net_margin_pct"] = fmt_pct(filtered["net_margin"] * 100)
    filtered["fcf_bn"] = fmt_bn(filtered["fcf"] / 1e9)
    filtered["roe_pct"] = fmt_pct(filtered["return_on_equity"] * 100)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[
                "Ticker", "Revenue ($B)", "Gross Margin",
                "Op Margin", "Net Margin", "FCF ($B)", "ROE"
            ],
            fill_color="#185FA5",
            font=dict(color="white", size=13),
            align="center"
        ),
        cells=dict(
            values=[
                filtered["ticker"],
                filtered["revenue_bn"],
                filtered["gross_margin_pct"],
                filtered["operating_margin_pct"],
                filtered["net_margin_pct"],
                filtered["fcf_bn"],
                filtered["roe_pct"],
            ],
            fill_color="#F1EFE8",
            align="center",
            font=dict(size=12)
        )
    )])

    fig.update_layout(
        title=f"Comparable Company Analysis — {year}",
        height=400
    )

    return fig