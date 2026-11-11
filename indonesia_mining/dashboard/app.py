
import os
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import textwrap
from plotly.subplots import make_subplots
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

st.set_page_config(
    page_title="Indonesia Mining Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional equity research theme
st.markdown("""


<style>
    /* =========================================
       1. GLOBAL THEME
    ========================================= */

    .stApp {
        background: #F5F5F7 !important;
        color: #202124 !important;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1600px;
    }

    h1, h2, h3 {
        color: #202124 !important;
        font-weight: 650;
        letter-spacing: -0.5px;
    }

    p, label {
        color: #44444B;
    }

    .section-label {
        color: #3478F6;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-bottom: 5px;
    }

    .dashboard-subtitle {
        color: #777780;
        font-size: 13px;
    }


    /* =========================================
       2. SIDEBAR
    ========================================= */

    [data-testid="stSidebar"] {
        background: #202124 !important;
        border-right: 1px solid #303238;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] label p {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"]
    div[role="radiogroup"] {
        gap: 5px;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"]
    div[role="radiogroup"] label {
        background: transparent !important;
        border-radius: 9px;
        padding: 7px 10px;
        transition: background 0.2s ease;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"]
    div[role="radiogroup"] label:hover {
        background: #34363B !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"]
    div[role="radiogroup"] label:has(input:checked) {
        background: #34363B !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"]
    div[role="radiogroup"] label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 600;
    }


    /* =========================================
       3. KPI CARDS
    ========================================= */

    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid #E8E8ED;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 22px rgba(0,0,0,0.09);
    }

    [data-testid="stMetricLabel"] {
        color: #777780 !important;
        font-size: 13px;
        font-weight: 500;
    }

    [data-testid="stMetricValue"] {
        color: #202124 !important;
        font-weight: 650;
    }

    [data-testid="stMetricDelta"] {
        font-weight: 600;
    }


    /* =========================================
       4. POSITIVE / NEGATIVE GRADIENT CARDS
    ========================================= */

    .best-performer {
        background: linear-gradient(
            120deg,
            #047857 0%,
            #059669 55%,
            #34D399 100%
        );
        border-radius: 14px;
        padding: 20px;
        color: #FFFFFF;
        box-shadow: 0 5px 15px rgba(5,150,105,0.18);
    }

    .worst-performer {
        background: linear-gradient(
            120deg,
            #B91C1C 0%,
            #DC2626 55%,
            #F87171 100%
        );
        border-radius: 14px;
        padding: 20px;
        color: #FFFFFF;
        box-shadow: 0 5px 15px rgba(220,38,38,0.18);
    }

    .best-performer *,
    .worst-performer * {
        color: #FFFFFF !important;
    }


    /* =========================================
       5. DATA TABLES
    ========================================= */

    [data-testid="stDataFrame"] {
        background: #FFFFFF !important;
        border: 1px solid #E5E5EA;
        border-radius: 12px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
        overflow: hidden;
    }

    [data-testid="stDataFrame"]:hover {
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    }


    /* =========================================
       6. PLOTLY CHARTS
    ========================================= */

    [data-testid="stPlotlyChart"] {
        background: #FFFFFF !important;
        border: 1px solid #E8E8ED;
        border-radius: 14px;
        padding: 8px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s ease;
    }

    [data-testid="stPlotlyChart"]:hover {
        box-shadow: 0 8px 20px rgba(0,0,0,0.07);
    }


    /* =========================================
       7. LISTED COMPANY - WHITE SELECTBOX
    ========================================= */

    [data-testid="stSelectbox"] [data-baseweb="select"] {
        background: #FFFFFF !important;
        border-radius: 10px !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #D9DDE5 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }

    /* Force internal layers, including arrow area */
    [data-testid="stSelectbox"] [data-baseweb="select"] > div > div {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSelectbox"] [data-baseweb="select"] input {
        color: #202124 !important;
        -webkit-text-fill-color: #202124 !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] svg {
        fill: #55555D !important;
        color: #55555D !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"]:hover > div {
        border-color: #3478F6 !important;
    }

    /* Dropdown menu */

    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        background: #FFFFFF !important;
        border: 1px solid #E5E5EA !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.10) !important;
    }

    [role="option"] {
        background: #FFFFFF !important;
        color: #30343B !important;
    }

    [role="option"]:hover {
        background: #F0F4FF !important;
    }

    [role="option"][aria-selected="true"] {
        background: #E8F0FE !important;
        color: #245CC5 !important;
    }


    /* =========================================
       8. HISTORICAL PERIOD - WHITE CONTROL
    ========================================= */

    [data-testid="stSegmentedControl"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #D9DDE5 !important;
        border-radius: 10px !important;
        padding: 4px !important;
    }

    [data-testid="stSegmentedControl"] > div {
        background: #FFFFFF !important;
        border-radius: 8px !important;
    }

    [data-testid="stSegmentedControl"] button,
    [data-testid="stSegmentedControl"] button > div {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #55555D !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 7px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }

    [data-testid="stSegmentedControl"] button p,
    [data-testid="stSegmentedControl"] button span {
        color: #55555D !important;
    }

    /* Selected option */

    [data-testid="stSegmentedControl"] button[aria-pressed="true"],
    [data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background: #EAF1FF !important;
        background-color: #EAF1FF !important;
        color: #245CC5 !important;
        border: 1px solid #D5E2FF !important;
        border-radius: 7px !important;
        font-weight: 650 !important;
    }

    [data-testid="stSegmentedControl"] button[aria-pressed="true"] p,
    [data-testid="stSegmentedControl"] button[aria-checked="true"] p,
    [data-testid="stSegmentedControl"] button[aria-pressed="true"] span,
    [data-testid="stSegmentedControl"] button[aria-checked="true"] span {
        color: #245CC5 !important;
    }

    [data-testid="stSegmentedControl"] button:hover {
        background: #F3F6FC !important;
        color: #245CC5 !important;
    }


    /* =========================================
       9. BUTTONS
    ========================================= */

    .stButton > button {
        border-radius: 9px;
        border: 1px solid #E5E5EA;
        background: #FFFFFF;
        color: #202124;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #3478F6;
        color: #3478F6;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }


    /* =========================================
       10. DIVIDERS & HEADER
    ========================================= */

    hr {
        border-color: #E5E5EA;
    }

    button[kind="header"] {
        color: #44444B;
    }

</style>


""", unsafe_allow_html=True)

# =========================================================
# DATABASE CONNECTION
# =========================================================

@st.cache_resource
def get_engine():

    required = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME"]

    missing = [key for key in required if not os.getenv(key)]

    if missing:
        raise ValueError(
            f"Missing database configuration: {', '.join(missing)}"
        )

    url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5433")),
        database=os.getenv("DB_NAME"),
    )

    return create_engine(url, pool_pre_ping=True)


@st.cache_data(ttl=300)
def load_performance():

    query = """
        SELECT *
        FROM analytics.mart_stock_performance
        ORDER BY daily_return_pct DESC
    """

    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=300)
def load_history(symbol):

    query = """
        SELECT *
        FROM analytics.mart_stock_history
        WHERE symbol = %(symbol)s
        ORDER BY trading_date
    """

    return pd.read_sql(
        query,
        get_engine(),
        params={"symbol": symbol}
    )

@st.cache_data(ttl=300)
def load_historical_performance():

    query = """
        SELECT
            symbol,
            latest_date,
            latest_close,
            return_1m_pct,
            return_3m_pct,
            return_6m_pct,
            return_1y_pct
        FROM analytics.mart_historical_performance
        ORDER BY return_1y_pct DESC
    """

    return pd.read_sql(query, get_engine())

@st.cache_data(ttl=300)
def load_comparison_history():

    query = """
        SELECT
            symbol,
            trading_date,
            daily_return_pct
        FROM analytics.mart_stock_history
        WHERE trading_date >= (
            CURRENT_DATE - INTERVAL '1 year'
        )
        ORDER BY symbol, trading_date
    """

    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=300)
def load_commodity_performance():
    query = """
        SELECT *
        FROM analytics.mart_commodity_performance
        ORDER BY daily_return_pct DESC
    """
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=300)
def load_commodity_history(symbol):
    query = """
        SELECT
            price_timestamp,
            trading_date,
            symbol,
            commodity_name,
            close_price,
            high_price,
            low_price,
            daily_return_pct,
            intraday_range_pct,
            calculated_sma_20,
            calculated_sma_50,
            calculated_volatility_20d,
            high_20d,
            low_20d
        FROM analytics.int_commodity_indicators
        WHERE symbol = %(symbol)s
        ORDER BY trading_date
    """
    return pd.read_sql(
        query,
        get_engine(),
        params={"symbol": symbol}
    )


@st.cache_data(ttl=300)
def load_all_commodity_history():
    query = """
        SELECT
            symbol,
            trading_date,
            close_price
        FROM analytics.int_commodity_indicators
        ORDER BY symbol, trading_date
    """
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=300)
def load_world_bank_commodity_performance():
    query = """
        SELECT *
        FROM analytics.mart_world_bank_commodity_performance
        ORDER BY monthly_return_rank
    """
    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=300)
def load_world_bank_commodity_history(symbol):
    query = """
        SELECT
            trading_date,
            symbol,
            commodity_name,
            close_price,
            monthly_return_pct,
            sma_3m,
            sma_6m,
            volatility_3m,
            high_12m,
            low_12m,
            unit,
            data_source,
            frequency
        FROM analytics.int_world_bank_commodity_indicators
        WHERE symbol = %(symbol)s
        ORDER BY trading_date
    """
    return pd.read_sql(
        query,
        get_engine(),
        params={"symbol": symbol}
    )

    query = """
        SELECT
            price_timestamp,
            trading_date,
            symbol,
            commodity_name,
            category,
            unit,
            close_price,
            high_price,
            low_price,
            daily_return_pct,
            intraday_range_pct,
            calculated_sma_20,
            calculated_sma_50,
            calculated_volatility_20d,
            high_20d,
            low_20d
        FROM analytics.int_commodity_indicators
        WHERE symbol = %(symbol)s
        ORDER BY price_timestamp
    """

    return pd.read_sql(
        query,
        get_engine(),
        params={"symbol": symbol}
    )

@st.cache_data(ttl=300)
def load_all_commodity_history():

    query = """
        SELECT
            symbol,
            trading_date,
            close_price
        FROM analytics.int_commodity_indicators
        ORDER BY symbol, trading_date
    """

    return pd.read_sql(query, get_engine())

@st.cache_data(ttl=300)
def load_jisdor_history():

    query = """
        SELECT trading_date, currency, nominal, jisdor_rate, buy_rate, sell_rate
        FROM public.jisdor_rates
        ORDER BY trading_date
    """

    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=300)
def load_bi_policy_history():

    query = """
        SELECT effective_date, policy_rate, source
        FROM public.bi_policy_rates
        ORDER BY effective_date
    """

    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=300)
def load_sensitivity_ranking():
    ranking_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "regression"
        / "sensitivity_ranking.csv"
    )

    if not ranking_path.exists():
        return pd.DataFrame()

    return pd.read_csv(ranking_path)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def format_idr(value):

    if pd.isna(value):
        return "-"

    return f"Rp {value:,.0f}"


def format_percentage(value):

    if pd.isna(value):
        return "-"

    return f"{value:+.2f}%"

def style_dark_table(df, percentage_columns=None):

    percentage_columns = percentage_columns or []

    def color_return(value):
        if pd.isna(value):
            return "color: #777780 !important"

        elif value > 0:
            return "color: #159A75 !important; font-weight: 600"

        elif value < 0:
            return "color: #E5484D !important; font-weight: 600"

        return "color: #777780 !important"

    styled = (
        df.style
        .set_properties(
            **{
                "background-color": "#FFFFFF",
                "color": "#30343B",
                "font-size": "13px",
                "padding": "12px 14px",
                "border": "none",
                "border-bottom": "1px solid #ECEEF2"
            }
        )
        .set_table_styles([
            {
                "selector": "th.col_heading",
                "props": [
                    ("background-color", "#F0F2F5"),
                    ("color", "#454B55"),
                    ("font-weight", "600"),
                    ("font-size", "12px"),
                    ("padding", "13px 14px"),
                    ("border-bottom", "1px solid #DDE1E7")
                ]
            },
            {
                "selector": "tbody tr:nth-child(even) td",
                "props": [
                    ("background-color", "#F8F9FB")
                ]
            },
            {
                "selector": "tbody tr:hover td",
                "props": [
                    ("background-color", "#EDF3FF")
                ]
            },
            {
                "selector": "table",
                "props": [
                    ("width", "100%"),
                    ("border-collapse", "separate"),
                    ("border-spacing", "0"),
                    ("border-radius", "10px"),
                    ("overflow", "hidden"),
                    ("border", "none")
                ]
            },
            {
                "selector": "th",
                "props": [
                    ("border", "none"),
                    ("border-bottom", "1px solid #E5E7EB")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("border", "none"),
                    ("border-bottom", "1px solid #F0F1F4")
                ]
            }
        ])
    )

    if percentage_columns:
        styled = styled.map(
            color_return,
            subset=percentage_columns
        )

    return styled

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("Created by RAIHAN DAFFA MUHAMMAD W")
st.sidebar.caption("INDONESIA MINING INTELLIGENCE")

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Market Overview",
        "Equity Analysis",
        "Stock Comparison",
        "Commodity Intelligence",
        "Sensitivity Analysis",
        "Macro & Monetary Intelligence",
        "Pipeline Information"
    ],
    label_visibility="collapsed"
)

st.sidebar.divider()

st.sidebar.markdown("### MARKET INFORMATION")
st.sidebar.caption("Exchange: Indonesia Stock Exchange")
st.sidebar.caption("Currency: Indonesian Rupiah")
st.sidebar.caption("Data provider: Yahoo Finance")

st.sidebar.divider()

st.sidebar.caption("Historical market data: 2023–Present")
st.sidebar.caption("Refresh interval: 5 minutes")


# =========================================================
# LOAD DATA
# =========================================================

try:

    performance = load_performance()
    historical_performance = load_historical_performance()
    comparison_history = load_comparison_history()
    commodity_performance = load_commodity_performance()
    commodity_history_all = load_all_commodity_history()
    world_bank_commodity_performance = load_world_bank_commodity_performance()
    jisdor_history = load_jisdor_history()
    bi_policy_history = load_bi_policy_history()

        # Calculate annualized volatility

    volatility_data = (
        comparison_history
        .groupby("symbol")["daily_return_pct"]
        .std()
        .mul(252 ** 0.5)
        .reset_index()
    )

    volatility_data.columns = [
        "symbol",
        "annualized_volatility_pct"
    ]

    comparison = historical_performance.merge(
        volatility_data,
        on="symbol",
        how="inner"
    )

    comparison = comparison[
        [
            "symbol",
            "return_1m_pct",
            "return_3m_pct",
            "return_6m_pct",
            "return_1y_pct",
            "annualized_volatility_pct"
        ]
    ].copy()

    performance["trading_date"] = pd.to_datetime(
        performance["trading_date"]
    )

    latest_date = performance["trading_date"].max()

    # =====================================================
    # HEADER
    # =====================================================

    st.title("Indonesia Mining Intelligence")

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Equity Research | Mining & Energy Sector | IDX'
        '</div>',
        unsafe_allow_html=True
    )

    st.write("")


    # =====================================================
    # PAGE 1: MARKET OVERVIEW
    # =====================================================

    if page == "Market Overview":

        st.markdown(
            '<div class="section-label">MARKET SNAPSHOT</div>',
            unsafe_allow_html=True
        )

        col_title, col_date = st.columns([3, 1])

        with col_title:
            st.subheader("Market Overview")

        with col_date:
            st.markdown(
                f"""
                <div style="
                    text-align: right;
                    color: #777780;
                    font-size: 16px;
                    font-weight: 600;
                    padding-top: 12px;
                    letter-spacing: 0.5px;
                ">
                    DATA AS OF · {latest_date.strftime('%d %b %Y').upper()}
                </div>
                """,
                unsafe_allow_html=True
            )

        # ==========================================
        # 1. MARKET OVERVIEW KPI
        # ==========================================

        best_stock = performance.loc[
            performance["daily_return_pct"].idxmax()
        ]

        worst_stock = performance.loc[
            performance["daily_return_pct"].idxmin()
        ]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Stocks Covered",
                performance["symbol"].nunique()
            )

        with col2:
            st.metric(
                "Average Daily Return",
                format_percentage(
                    performance["daily_return_pct"].mean()
                )
            )

        with col3:
            st.markdown(
                textwrap.dedent(f"""
                <div style="
                    background: linear-gradient(120deg, #047857, #059669 55%, #34D399);
                    padding: 20px;
                    border-radius: 14px;
                    min-height: 115px;
                    box-shadow: 0 5px 16px rgba(5,150,105,0.18);
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    gap: 8px;
                ">
                    <div style="color:#D1FAE5;font-size:11px;font-weight:700;letter-spacing:1px;">
                        BEST PERFORMER
                    </div>
                    <div style="color:#FFFFFF;font-size:27px;font-weight:700;">
                        {best_stock['symbol']}
                    </div>
                    <div style="color:#FFFFFF;font-size:15px;font-weight:700;">
                        ▲ {best_stock['daily_return_pct']:+.2f}%
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )

        with col4:
            st.markdown(
                textwrap.dedent(f"""
                <div style="
                    background: linear-gradient(120deg, #991B1B, #DC2626 55%, #F87171);
                    padding: 20px;
                    border-radius: 14px;
                    min-height: 115px;
                    box-shadow: 0 5px 16px rgba(220,38,38,0.18);
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    gap: 8px;
                ">
                    <div style="color:#FEE2E2;font-size:11px;font-weight:700;letter-spacing:1px;">
                        WORST PERFORMER
                    </div>
                    <div style="color:#FFFFFF;font-size:27px;font-weight:700;">
                        {worst_stock['symbol']}
                    </div>
                    <div style="color:#FFFFFF;font-size:15px;font-weight:700;">
                        ▼ {worst_stock['daily_return_pct']:+.2f}%
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )
        st.write("")

        # ==========================================
        # 2. DAILY EQUITY PERFORMANCE
        # ==========================================

        st.markdown("### Daily Equity Performance")

        chart_data = performance.sort_values(
            "daily_return_pct",
            ascending=True
        )

        colors = [
            "#159A75" if value >= 0 else "#E5484D"
            for value in chart_data["daily_return_pct"]
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=chart_data["symbol"],
                y=chart_data["daily_return_pct"],
                marker_color=colors,
                text=[
                    f"{value:+.2f}%"
                    for value in chart_data["daily_return_pct"]
                ],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(
                    color="#FFFFFF",
                    size=12,
                    family="Arial"
                ),
                marker_line=dict(
                    color="rgba(255,255,255,0.35)",
                    width=0.8
                ),
                cliponaxis=False
            )
        )

        fig.update_layout(
            template="plotly_white",
            height=430,
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(
                family="Arial, sans-serif",
                color="#30343B",
                size=13
            ),
            title_font=dict(
                color="#202124",
                size=16
            ),
            yaxis_title="Daily Return (%)",
            xaxis_title="Stock",
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor="#D1D5DB",
                tickfont=dict(
                    color="#4B5563",
                    size=11
                ),
                title_font=dict(color="#30343B")
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#E5E7EB",
                zeroline=True,
                zerolinecolor="#9CA3AF",
                zerolinewidth=1.2,
                tickfont=dict(
                    color="#4B5563",
                    size=11
                ),
                title_font=dict(color="#30343B")
            ),
            margin=dict(
                l=20,
                r=20,
                t=35,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ==========================================
        # 3. LATEST MARKET PERFORMANCE
        # ==========================================

        st.markdown("### Latest Market Performance")

        display_data = performance[
            [
                "symbol",
                "close_price",
                "daily_return_pct",
                "sma_20",
                "sma_50",
                "volatility_20d",
                "trend_signal"
            ]
        ].copy()

        display_data.columns = [
            "Ticker",
            "Closing Price",
            "Daily Return (%)",
            "SMA 20",
            "SMA 50",
            "Volatility 20D",
            "Trend Signal"
        ]

        latest_styled = style_dark_table(
            display_data,
            percentage_columns=[
                "Daily Return (%)",
                "Volatility 20D"
            ]
        ).format({
            "Closing Price": "{:,.2f}",
            "Daily Return (%)": "{:+.2f}%",
            "SMA 20": "{:,.2f}",
            "SMA 50": "{:,.2f}",
            "Volatility 20D": "{:.2f}%"
        })

        st.markdown(
            latest_styled
            .hide(axis="index")
            .set_table_attributes(
                'style="width:100%; table-layout:fixed;"'
            )
            .to_html(),
            unsafe_allow_html=True
        )

        st.caption(
            f"Latest available trading date: {latest_date.date()}"
        )

        st.write("")

        # ==========================================
        # 4. HISTORICAL EQUITY PERFORMANCE
        # ==========================================

        st.markdown("### Historical Equity Performance")

        historical_display = historical_performance[
            [
                "symbol",
                "return_1m_pct",
                "return_3m_pct",
                "return_6m_pct",
                "return_1y_pct"
            ]
        ].copy()

        historical_display.columns = [
            "Ticker",
            "1 Month",
            "3 Months",
            "6 Months",
            "1 Year"
        ]

        return_columns = [
            "1 Month",
            "3 Months",
            "6 Months",
            "1 Year"
        ]

        def color_return(value):

            if pd.isna(value):
                return "color: #777780"

            elif value > 0:
                return "color: #159A75; font-weight: 600"

            elif value < 0:
                return "color: #E5484D; font-weight: 600"

            return "color: #777780"

        historical_styled = (
            style_dark_table(historical_display)
            .map(
                color_return,
                subset=return_columns
            )
            .format({
                column: "{:+.2f}%"
                for column in return_columns
            })
            .set_table_attributes(
                'style="width:100%; border-collapse:collapse;"'
            )
            .hide(axis="index")
        )

        st.markdown(
            historical_styled.to_html(),
            unsafe_allow_html=True
        )

        st.caption(
            "Returns are calculated using adjusted closing prices. "
            "Historical performance does not guarantee future results."
        )


    # =====================================================
    # PAGE 2: EQUITY ANALYSIS
    # =====================================================

    elif page == "Equity Analysis":

        st.markdown(
            '<div class="section-label">INDIVIDUAL EQUITY RESEARCH</div>',
            unsafe_allow_html=True
        )

        st.subheader("Stock Analysis")

        selected_symbol = st.selectbox(
            "Select Listed Company",
            sorted(performance["symbol"].unique())
        )

        history = load_history(selected_symbol)

        history["trading_date"] = pd.to_datetime(
            history["trading_date"]
        )

        period = st.segmented_control(
            "Historical Period",
            options=["3 Months", "6 Months", "1 Year", "All History"],
            default="6 Months",
            selection_mode="single"
        )

        if period is None:
            period = "1 Year"


        days = {
            "3 Months": 90,
            "6 Months": 180,
            "1 Year": 365
        }

        if period != "All History":

            start_date = (
                history["trading_date"].max()
                - pd.Timedelta(days=days[period])
            )

            history = history[
                history["trading_date"] >= start_date
            ]

        latest = performance[
            performance["symbol"] == selected_symbol
        ].iloc[0]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Latest Close",
            format_idr(latest["close_price"])
        )

        daily_return = latest["daily_return_pct"]

        if pd.isna(daily_return):
            return_gradient = "linear-gradient(120deg, #475569, #64748B)"
            return_display = "N/A"
        elif daily_return > 0:
            return_gradient = "linear-gradient(120deg, #047857, #10B981, #34D399)"
            return_display = f"+{daily_return:.2f}%"
        elif daily_return < 0:
            return_gradient = "linear-gradient(120deg, #B91C1C, #EF4444, #F87171)"
            return_display = f"{daily_return:.2f}%"
        else:
            return_gradient = "linear-gradient(120deg, #475569, #64748B)"
            return_display = f"{daily_return:.2f}%"

        with col2:
            st.html(
                f"""
                <div style="
                    background: {return_gradient};
                    padding: 18px 20px;
                    border-radius: 13px;
                    min-height: 88px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.10);
                ">
                    <div style="color:rgba(255,255,255,0.9);
                                font-size:12px;
                                font-weight:600;
                                margin-bottom:10px;">
                        Daily Return
                    </div>
                    <div style="color:#FFFFFF;
                                font-size:25px;
                                font-weight:750;">
                        {return_display}
                    </div>
                </div>
                """
            )

        col3.metric(
            "SMA 20",
            format_idr(latest["sma_20"])
        )

        col4.metric(
            "Trend Signal",
            latest["trend_signal"]
        )

        # Historical Returns

        historical_stock = historical_performance[
            historical_performance["symbol"] == selected_symbol
        ].iloc[0]

        st.write("")
        st.markdown("### Historical Returns")

        historical_returns = [
            ("1 Month", historical_stock["return_1m_pct"]),
            ("3 Months", historical_stock["return_3m_pct"]),
            ("6 Months", historical_stock["return_6m_pct"]),
            ("1 Year", historical_stock["return_1y_pct"])
        ]

        ret_cols = st.columns(4)

        for col, (label, value) in zip(ret_cols, historical_returns):

            if pd.isna(value):
                gradient = "linear-gradient(135deg, #64748B, #94A3B8)"
                display_value = "N/A"

            elif value > 0:
                gradient = "linear-gradient(120deg, #047857, #10B981, #34D399)"
                display_value = f"+{value:.2f}%"

            elif value < 0:
                gradient = "linear-gradient(120deg, #B91C1C, #EF4444, #F87171)"
                display_value = f"{value:.2f}%"

            else:
                gradient = "linear-gradient(120deg, #475569, #64748B)"
                display_value = f"{value:.2f}%"

            with col:
                st.html(
                    f"""
                    <div style="
                        background: {gradient};
                        padding: 18px 20px;
                        border-radius: 13px;
                        min-height: 88px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.10);
                        margin-bottom: 8px;
                    ">
                        <div style="
                            color: rgba(255,255,255,0.9);
                            font-size: 12px;
                            font-weight: 600;
                            margin-bottom: 10px;
                        ">{label}</div>

                        <div style="
                            color: #FFFFFF;
                            font-size: 25px;
                            font-weight: 750;
                            letter-spacing: -0.5px;
                        ">{display_value}</div>
                    </div>
                    """
                )

        st.write("")

        # Candlestick chart

        st.markdown("### Price Development & Technical Indicators")

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.72, 0.28]
        )

        fig.add_trace(
            go.Candlestick(
                x=history["trading_date"],
                open=history["open_price"],
                high=history["high_price"],
                low=history["low_price"],
                close=history["close_price"],
                name="OHLC",
                increasing=dict(
                    line=dict(color="#059669", width=1),
                    fillcolor="#10B981"
                ),
                decreasing=dict(
                    line=dict(color="#DC2626", width=1),
                    fillcolor="#EF4444"
                )
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=history["trading_date"],
                y=history["sma_20"],
                name="SMA 20",
                mode="lines",
                line=dict(
                    color="#F59E0B",
                    width=2
                )
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=history["trading_date"],
                y=history["sma_50"],
                name="SMA 50",
                mode="lines",
                line=dict(
                    color="#2563EB",
                    width=2
                )
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Bar(
                x=history["trading_date"],
                y=history["volume"],
                name="Volume",
                marker_color="#60A5FA",
                marker_line=dict(
                    color="#3B82F6",
                    width=0.4
                ),
                opacity=0.85
            ),
            row=2,
            col=1
        )

        fig.update_layout(
            template="plotly_white",
            height=680,
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(
                family="Arial, sans-serif",
                color="#30343B",
                size=13
            ),
            xaxis_rangeslider_visible=False,
            hovermode="x unified",
            bargap=0.15,
            legend=dict(
                orientation="h",
                y=1.03,
                x=0,
                font=dict(
                    color="#30343B",
                    size=12
                )
            ),
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor="#D1D5DB",
                tickfont=dict(color="#4B5563", size=11)
            ),
            xaxis2=dict(
                showgrid=False,
                showline=True,
                linecolor="#D1D5DB",
                tickfont=dict(color="#4B5563", size=11)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#E5E7EB",
                zeroline=False,
                tickfont=dict(color="#4B5563", size=11),
                title_font=dict(color="#30343B")
            ),
            yaxis2=dict(
                showgrid=True,
                gridcolor="#E5E7EB",
                zeroline=False,
                tickfont=dict(color="#4B5563", size=10),
                title_font=dict(color="#30343B")
            ),
            margin=dict(l=25, r=25, t=55, b=25)
        )

        fig.update_yaxes(
            title_text="Price (IDR)",
            row=1,
            col=1
        )

        fig.update_yaxes(
            title_text="Volume",
            row=2,
            col=1
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # Historical Trading Data

        st.markdown("### Historical Trading Data")

        history_display = history.sort_values(
            "trading_date",
            ascending=False
        ).copy()

        percentage_columns = [
            "daily_return_pct",
            "intraday_range_pct",
            "volatility_20d"
        ]

        price_columns = [
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "adjusted_close",
            "sma_7",
            "sma_20",
            "sma_50",
            "high_20d",
            "low_20d"
        ]

        # Number formatting
        format_dict = {
            col: "{:,.2f}"
            for col in price_columns
            if col in history_display.columns
        }

        format_dict.update({
            col: "{:+.2f}%"
            for col in percentage_columns
            if col in history_display.columns
        })

        if "volume" in history_display.columns:
            format_dict["volume"] = "{:,.0f}"

        if "turnover_idr" in history_display.columns:
            format_dict["turnover_idr"] = "{:,.0f}"

        if "trading_date" in history_display.columns:
            format_dict["trading_date"] = lambda x: (
                x.strftime("%Y-%m-%d")
                if pd.notna(x) else "-"
            )

        # Conditional coloring for daily returns
        def color_daily_return(value):

            if pd.isna(value):
                return "color: #777780"

            elif value > 0:
                return "color: #059669; font-weight: 600"

            elif value < 0:
                return "color: #DC2626; font-weight: 600"

            return "color: #777780"

        # Build styled table
        styled_history = (
            style_dark_table(
                history_display,
                percentage_columns=percentage_columns
            )
            .map(
                color_daily_return,
                subset=["daily_return_pct"]
            )
            .format(format_dict)
        )

        st.table(styled_history)

    # =====================================================
    # PAGE 3: STOCK COMPARISON
    # =====================================================

    elif page == "Stock Comparison":

        st.markdown(
            '<div class="section-label">CROSS-EQUITY ANALYSIS</div>',
            unsafe_allow_html=True
        )

        st.subheader("Stock Performance Comparison")

        selected_period = st.segmented_control(
            "Select Performance Period",
            options=["1 Month", "3 Months", "6 Months", "1 Year"],
            default="1 Year",
            selection_mode="single"
        )

        if selected_period is None:
            selected_period = "1 Year"

        return_columns = {
            "1 Month": "return_1m_pct",
            "3 Months": "return_3m_pct",
            "6 Months": "return_6m_pct",
            "1 Year": "return_1y_pct"
        }

        selected_return_column = return_columns[selected_period]

        st.markdown(f"### Risk vs {selected_period} Return")

        # Match volatility period with selected return period

        period_days = {
            "1 Month": 30,
            "3 Months": 90,
            "6 Months": 180,
            "1 Year": 365
        }

        comparison_history["trading_date"] = pd.to_datetime(
            comparison_history["trading_date"]
        )

        latest_trading_date = comparison_history["trading_date"].max()

        start_date = (
            latest_trading_date
            - pd.Timedelta(days=period_days[selected_period])
        )

        selected_history = comparison_history[
            comparison_history["trading_date"] >= start_date
        ]

        period_volatility = (
            selected_history
            .groupby("symbol")["daily_return_pct"]
            .std()
            .mul(252 ** 0.5)
            .reset_index()
        )

        period_volatility.columns = [
            "symbol",
            "annualized_volatility_pct"
        ]

        comparison = (
            comparison
            .drop(columns=["annualized_volatility_pct"])
            .merge(period_volatility, on="symbol", how="inner")
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=comparison["annualized_volatility_pct"],
                y=comparison[selected_return_column],
                mode="markers+text",
                text=comparison["symbol"],
                textposition="top center",
                textfont=dict(
                    color="#30343B",
                    size=11
                ),
                marker=dict(
                    size=16,
                    color=comparison[selected_return_column],
                    colorscale=[
                        [0, "#E5484D"],
                        [0.5, "#F5B942"],
                        [1, "#16A36A"]
                    ],
                    showscale=True,
                    colorbar=dict(
                        title=dict(
                            text=f"{selected_period}<br>Return (%)",
                            font=dict(color="#30343B", size=11)
                        ),
                        tickfont=dict(color="#4B5563", size=10),
                        outlinecolor="#D1D5DB"
                    ),
                    line=dict(
                        width=1.2,
                        color="#FFFFFF"
                    ),
                    opacity=0.9
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Annualized Volatility: %{x:.2f}%<br>"
                    f"{selected_period} Return: "
                    "%{y:.2f}%"
                    "<extra></extra>"
                )
            )
        )

        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="#64748B"
        )

        fig.update_layout(
            template="plotly_white",
            title=dict(
                text=f"Risk vs {selected_period} Return",
                font=dict(
                    color="#202124",
                    size=17
                )
            ),
            xaxis_title="Annualized Volatility (%)",
            yaxis_title=f"{selected_period} Historical Return (%)",
            height=550,
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(
                family="Arial, sans-serif",
                color="#30343B",
                size=13
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor="#E5E7EB",
                zeroline=True,
                zerolinecolor="#9CA3AF",
                showline=True,
                linecolor="#D1D5DB",
                tickfont=dict(color="#4B5563", size=11),
                title_font=dict(color="#30343B")
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#E5E7EB",
                zeroline=True,
                zerolinecolor="#9CA3AF",
                showline=True,
                linecolor="#D1D5DB",
                tickfont=dict(color="#4B5563", size=11),
                title_font=dict(color="#30343B")
            ),
            margin=dict(l=30, r=30, t=50, b=30)
        )


        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Historical Performance Comparison")

        comparison_display = comparison[
            [
                "symbol",
                "return_1m_pct",
                "return_3m_pct",
                "return_6m_pct",
                "return_1y_pct",
                "annualized_volatility_pct"
            ]
        ].copy()

        selected_column_name = f"{selected_period} Selected (%)"

        comparison_display[selected_column_name] = comparison[
            selected_return_column
        ]

        comparison_display.columns = [
            "Ticker",
            "1 Month (%)",
            "3 Months (%)",
            "6 Months (%)",
            "1 Year (%)",
            "Annualized Volatility (%)",
            selected_column_name
        ]

        percentage_columns = [
            "1 Month (%)",
            "3 Months (%)",
            "6 Months (%)",
            "1 Year (%)",
            "Annualized Volatility (%)",
            selected_column_name
        ]

        format_dict = {
            col: "{:+.2f}%"
            for col in percentage_columns
        }

        def color_comparison_return(value):
            if pd.isna(value):
                return "color: #777780;"

            if value > 0:
                return "color: #059669; font-weight: 700;"

            if value < 0:
                return "color: #DC2626; font-weight: 700;"

            return "color: #777780;"

        # Apply table styling
        styled_comparison = (
            comparison_display.style
            .format(
                {
                    "1 Month (%)": "{:+.2f}%",
                    "3 Months (%)": "{:+.2f}%",
                    "6 Months (%)": "{:+.2f}%",
                    "1 Year (%)": "{:+.2f}%",
                    "Annualized Volatility (%)": "{:.2f}%",
                    selected_column_name: "{:+.2f}%"
                },
                na_rep="—"
            )
            .set_properties(
                **{
                    "background-color": "#FFFFFF",
                    "color": "#30343B",
                    "font-size": "13px",
                    "padding": "12px 14px",
                    "border": "none",
                    "border-bottom": "1px solid #ECEEF2"
                }
            )
            .set_table_styles([
                {
                    "selector": "th.col_heading",
                    "props": [
                        ("background-color", "#F0F2F5"),
                        ("color", "#454B55"),
                        ("font-weight", "600"),
                        ("font-size", "12px"),
                        ("padding", "12px 14px"),
                        ("border", "none"),
                        ("border-bottom", "1px solid #DDE1E7")
                    ]
                },
                {
                    "selector": "tbody td",
                    "props": [
                        ("border", "none"),
                        ("border-bottom", "1px solid #ECEEF2")
                    ]
                },
                {
                    "selector": "tbody tr:nth-child(even) td",
                    "props": [
                        ("background-color", "#F8F9FB")
                    ]
                },
                {
                    "selector": "table",
                    "props": [
                        ("width", "100%"),
                        ("border-collapse", "separate"),
                        ("border-spacing", "0"),
                        ("border-radius", "10px"),
                        ("overflow", "hidden")
                    ]
                }
            ])
        )

        # Color positive and negative returns
        def color_comparison_return(value):
            if pd.isna(value):
                return "color: #777780;"

            if value > 0:
                return "color: #059669; font-weight: 700;"

            if value < 0:
                return "color: #DC2626; font-weight: 700;"

            return "color: #777780;"

        styled_comparison = styled_comparison.map(
            color_comparison_return,
            subset=percentage_columns
        )

        # Force table to use full available width
        styled_comparison = styled_comparison.set_table_attributes(
            'style="width:100%; min-width:100%; table-layout:fixed;"'
        )

        table_html = styled_comparison.hide(axis="index").to_html()

        st.html(table_html)

        st.caption(
            "Volatility is estimated from daily returns over the "
            "latest one-year period and annualized using √252. "
            "Historical returns are not guarantees of future performance."
        )
    # =====================================================
    # PAGE 4: COMMODITY INTELLIGENCE
    # =====================================================

    elif page == "Commodity Intelligence":

        st.markdown(
            '<div class="section-label">GLOBAL COMMODITY RESEARCH</div>',
            unsafe_allow_html=True
        )

        st.subheader("Commodity Intelligence")

        if commodity_performance.empty:
            st.warning("No commodity data available.")
        else:

            # Commodity market overview

            st.markdown("### Global Commodity Market Overview")

            # Yahoo Finance - Daily data
            yahoo_overview = commodity_performance[
                [
                    "symbol",
                    "close_price",
                    "unit",
                    "daily_return_pct",
                    "sma_20",
                    "sma_50",
                    "trend_signal"
                ]
            ].copy()

            yahoo_overview.columns = [
                "Commodity",
                "Latest Price",
                "Unit",
                "Return (%)",
                "Short MA",
                "Long MA",
                "Trend"
            ]

            yahoo_overview["MA Window"] = "20D / 50D"
            yahoo_overview["Source"] = "Yahoo Finance"
            yahoo_overview["Frequency"] = "Daily"


            # World Bank - Monthly data
            wb_overview = world_bank_commodity_performance[
                [
                    "symbol",
                    "close_price",
                    "unit",
                    "monthly_return_pct",
                    "sma_3m",
                    "sma_6m",
                    "trend_signal"
                ]
            ].copy()

            wb_overview.columns = [
                "Commodity",
                "Latest Price",
                "Unit",
                "Return (%)",
                "Short MA",
                "Long MA",
                "Trend"
            ]

            wb_overview["MA Window"] = "3M / 6M"
            wb_overview["Source"] = "World Bank"
            wb_overview["Frequency"] = "Monthly"


            # Combine both data sources
            overview = pd.concat(
                [yahoo_overview, wb_overview],
                ignore_index=True
            )

            # Display order
            overview = overview[
                [
                    "Commodity",
                    "Latest Price",
                    "Unit",
                    "Return (%)",
                    "Short MA",
                    "Long MA",
                    "MA Window",
                    "Trend",
                    "Source",
                    "Frequency"
                ]
            ]

            # Sort instruments
            commodity_order = ["GOLD", "COPPER", "BRENT", "NICKEL", "COAL"]

            overview["Commodity"] = pd.Categorical(
                overview["Commodity"],
                categories=commodity_order,
                ordered=True
            )

            overview = overview.sort_values("Commodity")
            overview["Commodity"] = overview["Commodity"].astype(str)


            # Display formatted table - Apple-inspired light theme

            def color_overview_return(value):
                if pd.isna(value):
                    return "color: #777780;"

                if value > 0:
                    return "color: #159A75; font-weight: 600;"

                if value < 0:
                    return "color: #E5484D; font-weight: 600;"

                return "color: #777780;"


            overview_format = {
                "Latest Price": "{:,.2f}",
                "Return (%)": "{:+.2f}%",
                "Short MA": "{:,.2f}",
                "Long MA": "{:,.2f}"
            }

            # Color formatting
            def color_overview_return(value):
                if pd.isna(value):
                    return "color: #777780;"

                if value > 0:
                    return "color: #159A75; font-weight: 600;"

                if value < 0:
                    return "color: #E5484D; font-weight: 600;"

                return "color: #777780;"


            def color_trend(value):
                if value == "Bullish":
                    return "color: #159A75; font-weight: 700;"
                elif value == "Bearish":
                    return "color: #E5484D; font-weight: 700;"

                return "color: #777780; font-weight: 600;"


            # Number formatting
            overview_format = {
                "Latest Price": "{:,.2f}",
                "Return (%)": "{:+.2f}%",
                "Short MA": "{:,.2f}",
                "Long MA": "{:,.2f}"
            }


            # Apple-inspired light theme table
            styled_overview = (
                overview.style
                .hide(axis="index")
                .format(overview_format, na_rep="—")
                .set_properties(**{
                    "background-color": "#FFFFFF",
                    "color": "#30343B",
                    "font-size": "13px",
                    "padding": "11px 14px",
                    "border": "none",
                    "border-bottom": "1px solid #ECEEF2",
                    "text-align": "center",
                    "white-space": "nowrap"
                })
                .map(
                    color_overview_return,
                    subset=["Return (%)"]
                )
                .map(
                    color_trend,
                    subset=["Trend"]
                )
                .set_table_styles([
                    {
                        "selector": "th",
                        "props": [
                            ("background-color", "#F0F2F5"),
                            ("color", "#454B55"),
                            ("font-weight", "600"),
                            ("font-size", "12px"),
                            ("padding", "13px 14px"),
                            ("border-bottom", "1px solid #DDE1E7"),
                            ("text-align", "center"),
                            ("white-space", "nowrap")
                        ]
                    },
                    {
                        "selector": "tbody tr:nth-child(even) td",
                        "props": [
                            ("background-color", "#F8F9FB")
                        ]
                    },
                    {
                        "selector": "tbody tr:hover td",
                        "props": [
                            ("background-color", "#EDF3FF")
                        ]
                    },
                    {
                        "selector": "table",
                        "props": [
                            ("width", "100%"),
                            ("min-width", "100%"),
                            ("border-collapse", "separate"),
                            ("border-spacing", "0"),
                            ("border-radius", "10px"),
                            ("overflow", "hidden"),
                            ("border", "1px solid #E5E5EA"),
                            ("table-layout", "auto")
                        ]
                    }
                ])
                .set_table_attributes(
                    'style="width:100%; min-width:100%;"'
                )
            )

            st.html(styled_overview.to_html())

            st.write("")
            st.divider()

            # Commodity selector
            selected_commodity = st.segmented_control(
                "Select Commodity",
                options=["GOLD", "COPPER", "BRENT", "NICKEL", "COAL"],
                default="GOLD",
                selection_mode="single"
            )

            if selected_commodity is None:
                selected_commodity = "GOLD"


            # Select data source based on commodity
            if selected_commodity in ["GOLD", "COPPER", "BRENT"]:

                latest = commodity_performance[
                    commodity_performance["symbol"] == selected_commodity
                ].iloc[0]

                commodity_history = load_commodity_history(
                    selected_commodity
                )

                return_label = "Daily Return"
                return_value = format_percentage(latest["daily_return_pct"])

                sma_label = "SMA 20"
                sma_value = f"${latest['sma_20']:,.2f}"

                sma_short = "calculated_sma_20"
                sma_long = "calculated_sma_50"

                return_column = "daily_return_pct"
                volatility_column = "calculated_volatility_20d"
                range_column = "intraday_range_pct"

                sma_short_label = "SMA 20"
                sma_long_label = "SMA 50"

                source_caption = (
                    "Source: Yahoo Finance via yfinance. "
                    "Prices represent futures market observations, "
                    "not guaranteed real-time quotes."
                )

            else:

                latest = world_bank_commodity_performance[
                    world_bank_commodity_performance["symbol"] == selected_commodity
                ].iloc[0]

                commodity_history = load_world_bank_commodity_history(
                    selected_commodity
                )

                return_label = "Monthly Return"
                return_value = format_percentage(latest["monthly_return_pct"])

                sma_label = "SMA 3 Months"
                sma_value = f"${latest['sma_3m']:,.2f}"

                sma_short = "sma_3m"
                sma_long = "sma_6m"

                return_column = "monthly_return_pct"
                volatility_column = "volatility_3m"
                range_column = None

                sma_short_label = "SMA 3M"
                sma_long_label = "SMA 6M"

                source_caption = (
                    "Source: World Bank Pink Sheet. "
                    "Monthly commodity benchmark prices; "
                    "Australian Coal is a global benchmark proxy."
                )


            # KPI section - Dynamic Apple-inspired cards

            col1, col2, col3, col4 = st.columns(4)

            # Determine dynamic colors
            return_numeric = float(latest[return_column])

            if return_numeric > 0:
                return_color = "#159A75"
            elif return_numeric < 0:
                return_color = "#E5484D"
            else:
                return_color = "#777780"

            trend_signal = str(latest["trend_signal"])

            if trend_signal == "Bullish":
                trend_color = "#159A75"
            elif trend_signal == "Bearish":
                trend_color = "#E5484D"
            else:
                trend_color = "#777780"


            # Reusable KPI card
            def render_kpi_card(column, label, value, value_color="#30343B"):
                column.markdown(
                    f"""
                    <div style="
                        background: #FFFFFF;
                        border: 1px solid #E5E5EA;
                        border-radius: 14px;
                        padding: 18px 16px;
                        min-height: 88px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
                    ">
                        <div style="
                            color: #777780;
                            font-size: 12px;
                            margin-bottom: 8px;
                        ">
                            {label}
                        </div>
                        <div style="
                            color: {value_color};
                            font-size: 25px;
                            font-weight: 700;
                            line-height: 1.2;
                        ">
                            {value}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # Render four KPI cards
            render_kpi_card(
                col1,
                "Latest Price",
                f"${latest['close_price']:,.2f}"
            )

            render_kpi_card(
                col2,
                return_label,
                return_value,
                return_color
            )

            render_kpi_card(
                col3,
                sma_label,
                sma_value
            )

            render_kpi_card(
                col4,
                "Trend Signal",
                trend_signal,
                trend_color
            )


            st.caption(
                f"Commodity: {latest['commodity_name']} | "
                f"Unit: {latest['unit']} | "
                f"Latest observation: {latest['trading_date']} | "
                f"Frequency: {'Daily' if selected_commodity in ['GOLD', 'COPPER', 'BRENT'] else 'Monthly'}"
            )

            st.write("")


            # Historical price chart
            st.markdown("### Historical Price Development")

            period = st.segmented_control(
                "Historical Period",
                options=["3 Months", "6 Months", "1 Year", "All History"],
                default="1 Year",
                selection_mode="single"
            )

            if period is None:
                period = "1 Year"

            if period != "All History":

                months = {
                    "3 Months": 3,
                    "6 Months": 6,
                    "1 Year": 12
                }

                commodity_history["trading_date"] = pd.to_datetime(
                    commodity_history["trading_date"]
                )

                start_date = (
                    commodity_history["trading_date"].max()
                    - pd.DateOffset(months=months[period])
                )

                commodity_history = commodity_history[
                    commodity_history["trading_date"] >= start_date
                ]


            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=commodity_history["trading_date"],
                    y=commodity_history["close_price"],
                    name="Closing Price",
                    mode="lines",
                    line=dict(
                        color="#159A75",
                        width=2.5
                    )
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=commodity_history["trading_date"],
                    y=commodity_history[sma_short],
                    name=sma_short_label,
                    mode="lines",
                    line=dict(
                        color="#3478F6",
                        width=2
                    )
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=commodity_history["trading_date"],
                    y=commodity_history[sma_long],
                    name=sma_long_label,
                    mode="lines",
                    line=dict(
                        color="#F59E0B",
                        width=2
                    )
                )
            )

            fig.update_layout(
                template="plotly_white",
                height=500,
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(
                    family="Arial, sans-serif",
                    color="#30343B",
                    size=13
                ),
                yaxis_title=f"Price ({latest['unit']})",
                xaxis_title="Observation Date",
                xaxis=dict(
                    showgrid=False,
                    showline=True,
                    linecolor="#D1D5DB",
                    tickfont=dict(
                        color="#4B5563",
                        size=11
                    ),
                    title_font=dict(color="#30343B")
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="#E5E7EB",
                    zerolinecolor="#9CA3AF",
                    tickfont=dict(
                        color="#4B5563",
                        size=11
                    ),
                    title_font=dict(color="#30343B")
                ),
                legend=dict(
                    orientation="h",
                    y=1.02,
                    font=dict(
                        color="#30343B",
                        size=12
                    )
                ),
                margin=dict(l=20, r=20, t=50, b=20)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # Historical data table
            st.markdown("### Historical Commodity Data")

            if selected_commodity in ["GOLD", "COPPER", "BRENT"]:

                display_columns = [
                    "trading_date",
                    "close_price",
                    "daily_return_pct",
                    "intraday_range_pct",
                    "calculated_sma_20",
                    "calculated_sma_50",
                    "calculated_volatility_20d"
                ]

                percentage_columns = [
                    "daily_return_pct",
                    "intraday_range_pct",
                    "calculated_volatility_20d"
                ]

                price_columns = [
                    "close_price",
                    "calculated_sma_20",
                    "calculated_sma_50"
                ]

            else:

                display_columns = [
                    "trading_date",
                    "close_price",
                    "monthly_return_pct",
                    "sma_3m",
                    "sma_6m",
                    "volatility_3m"
                ]

                percentage_columns = [
                    "monthly_return_pct",
                    "volatility_3m"
                ]

                price_columns = [
                    "close_price",
                    "sma_3m",
                    "sma_6m"
                ]


            # Prepare data
            historical_display = commodity_history[
                display_columns
            ].copy()

            historical_display["trading_date"] = pd.to_datetime(
                historical_display["trading_date"],
                errors="coerce"
            ).dt.strftime("%Y-%m-%d")

            historical_display = historical_display.sort_values(
                "trading_date",
                ascending=False
            )

            # Ensure numeric columns
            for col in price_columns + percentage_columns:
                historical_display[col] = pd.to_numeric(
                    historical_display[col],
                    errors="coerce"
                )

            # Number formatting
            format_dict = {
                col: "{:,.2f}"
                for col in price_columns
            }

            format_dict.update({
                col: "{:+.2f}%"
                for col in percentage_columns
            })


            # Display historical commodity data - Light Theme

            def color_return(value):
                if pd.isna(value):
                    return "color: #777780;"

                if value > 0:
                    return "color: #159A75; font-weight: 600;"

                if value < 0:
                    return "color: #E5484D; font-weight: 600;"

                return "color: #777780;"


            styled_commodity_history = (
                historical_display.style
                .hide(axis="index")
                .format(format_dict, na_rep="—")
                .map(color_return, subset=percentage_columns)
                .set_properties(**{
                    "background-color": "#FFFFFF",
                    "color": "#30343B",
                    "font-size": "13px",
                    "padding": "11px 14px",
                    "border": "none",
                    "border-bottom": "1px solid #ECEEF2",
                    "text-align": "right"
                })
                .set_table_styles([
                    {
                        "selector": "th",
                        "props": [
                            ("background-color", "#F0F2F5"),
                            ("color", "#454B55"),
                            ("font-weight", "600"),
                            ("font-size", "12px"),
                            ("padding", "13px 14px"),
                            ("border-bottom", "1px solid #DDE1E7"),
                            ("text-align", "center"),
                            ("white-space", "nowrap")
                        ]
                    },
                    {
                        "selector": "tbody tr:nth-child(even) td",
                        "props": [
                            ("background-color", "#F8F9FB")
                        ]
                    },
                    {
                        "selector": "tbody tr:hover td",
                        "props": [
                            ("background-color", "#EDF3FF"
                            )
                        ]
                    },
                    {
                        "selector": "table",
                        "props": [
                            ("width", "100%"),
                            ("min-width", "100%"),
                            ("border-collapse", "separate"),
                            ("border-spacing", "0"),
                            ("border-radius", "10px"),
                            ("overflow", "hidden"),
                            ("border", "1px solid #E5E5EA"),
                            ("table-layout", "auto")
                        ]
                    }
                ])
                .set_table_attributes(
                    'style="width:100%; min-width:100%;"'
                )
            )

            st.html(styled_commodity_history.to_html())

    # =====================================================
    # PAGE 5: SENSITIVITY ANALYSIS
    # =====================================================

    elif page == "Sensitivity Analysis":

        st.markdown(
            '<div class="section-label">MULTIFACTOR EQUITY RESEARCH</div>',
            unsafe_allow_html=True
        )
        st.subheader("Mining Equity Sensitivity Analysis")
        st.caption(
            "Statistical relationships between mining equity returns, "
            "global commodity returns, and USD/IDR movements."
        )

        sensitivity = load_sensitivity_ranking()

        if sensitivity.empty:
            st.warning(
                "Sensitivity ranking file was not found. "
                "Expected: data/processed/regression/sensitivity_ranking.csv"
            )
        else:
            factor_labels = {
                "Gold": "gold_return_pct",
                "Brent": "brent_return_pct",
                "Copper": "copper_return_pct",
                "JISDOR (USD/IDR)": "jisdor_return_pct",
                "BI Rate": "bi_rate_change_bps"
            }

            factor_label = st.selectbox(
                "Select External Factor",
                list(factor_labels.keys()),
                index=0
            )
            selected_factor = factor_labels[factor_label]

            factor_data = sensitivity[
                sensitivity["variable"] == selected_factor
            ].copy()

            # Colored KPI cards, consistent with the Macro & Market Overview style.
            kpis = [
                ("FDR-SIGNIFICANT", f"{int(sensitivity['fdr_significant'].sum())}",
                 "Relationships after BH correction",
                 "linear-gradient(120deg,#1D4ED8,#2563EB 55%,#60A5FA)", "#DBEAFE"),
                ("ROBUST RELATIONSHIPS", f"{int(sensitivity['robust_significant'].sum())}",
                 "Same direction, p < 0.05 in robustness sample",
                 "linear-gradient(120deg,#047857,#059669 55%,#34D399)", "#D1FAE5"),
                ("FACTORS COVERED", f"{sensitivity['variable'].nunique()}",
                 "External market and monetary factors",
                 "linear-gradient(120deg,#6D28D9,#7C3AED 55%,#A78BFA)", "#EDE9FE"),
            ]
            kcols = st.columns(3)
            for col, (label, value, detail, gradient, soft) in zip(kcols, kpis):
                with col:
                    st.markdown(textwrap.dedent(f"""
                        <div style="background:{gradient};padding:20px;border-radius:14px;
                            min-height:118px;box-shadow:0 5px 16px rgba(0,0,0,.12);
                            display:flex;flex-direction:column;justify-content:center;gap:8px;">
                            <div style="color:{soft};font-size:11px;font-weight:700;letter-spacing:1px;">{label}</div>
                            <div style="color:#FFFFFF;font-size:27px;font-weight:750;line-height:1.15;">{value}</div>
                            <div style="color:#FFFFFF;font-size:12px;font-weight:600;opacity:.95;">{detail}</div>
                        </div>
                    """), unsafe_allow_html=True)

            st.markdown("### Equity Sensitivity Ranking")

            show_robust_only = st.checkbox(
                "Show only relationships consistent in robustness sample",
                value=True
            )

            if show_robust_only and not factor_data.empty:
                factor_data = factor_data[
                    factor_data["robust_significant"].astype(bool)
                ]

            if factor_data.empty:
                st.info(
                    f"No qualifying FDR-significant and robust relationships "
                    f"are available for {factor_label}."
                )
            else:
                factor_data = factor_data.sort_values(
                    "coefficient",
                    ascending=True
                )

                chart_colors = [
                    "#159A75" if value >= 0 else "#E5484D"
                    for value in factor_data["coefficient"]
                ]

                fig = go.Figure(
                    go.Bar(
                        x=factor_data["coefficient"],
                        y=factor_data["symbol"],
                        orientation="h",
                        marker_color=chart_colors,
                        text=[
                            f"{value:+.3f}"
                            for value in factor_data["coefficient"]
                        ],
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate=(
                            "<b>%{y}</b><br>"
                            "Coefficient: %{x:.4f}"
                            "<extra></extra>"
                        )
                    )
                )

                fig.add_vline(
                    x=0,
                    line_dash="dash",
                    line_color="#64748B"
                )
                fig.update_layout(
                    template="plotly_white",
                    height=max(380, 35 * len(factor_data) + 100),
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    xaxis_title="Regression Coefficient",
                    yaxis_title="Issuer",
                    showlegend=False,
                    margin=dict(l=105, r=90, t=35, b=75),
                    font=dict(
                        family="Arial, sans-serif",
                        color="#1F2937",
                        size=13
                    ),
                    xaxis=dict(
                        title=dict(text="Regression Coefficient", font=dict(color="#111827", size=14)),
                        tickfont=dict(color="#1F2937", size=12),
                        showgrid=True,
                        gridcolor="#CBD5E1",
                        zeroline=True,
                        zerolinecolor="#64748B",
                        showline=True,
                        linecolor="#64748B",
                        ticks="outside",
                        tickcolor="#64748B"
                    ),
                    yaxis=dict(
                        title=dict(text="Issuer", font=dict(color="#111827", size=14)),
                        tickfont=dict(color="#1F2937", size=12),
                        showgrid=False,
                        automargin=True
                    )
                )
                st.plotly_chart(fig, use_container_width=True)

                display_columns = [
                    "symbol",
                    "coefficient",
                    "q_value",
                    "short_coefficient",
                    "short_p_value",
                    "robust_significant"
                ]
                display_data = factor_data[display_columns].copy()
                display_data.columns = [
                    "Ticker",
                    "Full-sample coefficient",
                    "FDR q-value",
                    "Robustness coefficient",
                    "Robustness p-value",
                    "Robust"
                ]

                display_data["Robust"] = display_data["Robust"].map(
                    {True: "Yes", False: "No"}
                )

                table_format = {
                    "Full-sample coefficient": "{:+.4f}",
                    "FDR q-value": "{:.3g}",
                    "Robustness coefficient": "{:+.4f}",
                    "Robustness p-value": "{:.3g}"
                }

                def style_coefficient(value):
                    if pd.isna(value):
                        return "color:#64748B;"
                    if value > 0:
                        return "color:#047857;font-weight:700;"
                    if value < 0:
                        return "color:#DC2626;font-weight:700;"
                    return "color:#334155;font-weight:600;"

                styled_sensitivity = (
                    display_data.style
                    .hide(axis="index")
                    .format(table_format, na_rep="—")
                    .map(style_coefficient, subset=[
                        "Full-sample coefficient", "Robustness coefficient"
                    ])
                    .set_properties(**{
                        "background-color": "#FFFFFF",
                        "color": "#1F2937",
                        "font-size": "13px",
                        "padding": "12px 14px",
                        "border": "none",
                        "border-bottom": "1px solid #E5E7EB",
                        "text-align": "right"
                    })
                    .set_table_styles([
                        {
                            "selector": "th",
                            "props": [
                                ("background-color", "#EFF4FA"),
                                ("color", "#1E293B"),
                                ("font-weight", "700"),
                                ("font-size", "12px"),
                                ("padding", "13px 14px"),
                                ("border-bottom", "2px solid #CBD5E1"),
                                ("text-align", "left"),
                                ("white-space", "nowrap")
                            ]
                        },
                        {
                            "selector": "tbody tr:nth-child(even) td",
                            "props": [("background-color", "#F8FAFC")]
                        },
                        {
                            "selector": "tbody tr:hover td",
                            "props": [("background-color", "#EAF2FF")]
                        },
                        {
                            "selector": "table",
                            "props": [
                                ("width", "100%"),
                                ("border-collapse", "separate"),
                                ("border-spacing", "0"),
                                ("border-radius", "10px"),
                                ("overflow", "hidden"),
                                ("border", "1px solid #E2E8F0"),
                                ("table-layout", "auto")
                            ]
                        }
                    ])
                    .set_table_attributes('style="width:100%;"')
                )

                st.html(styled_sensitivity.to_html())

                st.download_button(
                    "Download displayed ranking (CSV)",
                    data=display_data.to_csv(index=False).encode("utf-8"),
                    file_name="mining_equity_sensitivity_ranking.csv",
                    mime="text/csv"
                )

            st.markdown("### Methodology")
            st.caption(
                "Coefficients are estimated using per-stock OLS models with "
                "Newey-West HAC standard errors. FDR q-values use the "
                "Benjamini–Hochberg procedure across 155 factor–issuer tests "
                "in the full sample. Robustness indicates the coefficient "
                "keeps the same direction and has p < 0.05 in the sample "
                "restricted to intervals of no more than three calendar days. "
                "These are conditional associations, not causal effects or "
                "investment recommendations."
            )

    # =====================================================
    # PAGE 6: MACRO & MONETARY INTELLIGENCE
    # =====================================================

    elif page == "Macro & Monetary Intelligence":

        st.markdown(
            '<div class="section-label">MACROECONOMIC & MONETARY MONITORING</div>',
            unsafe_allow_html=True
        )
        st.subheader("Macro & Monetary Intelligence")
        st.caption(
            "Monitoring Indonesia's USD/IDR reference exchange rate and "
            "Bank Indonesia's policy-rate decisions."
        )

        jisdor = jisdor_history.copy()
        policy = bi_policy_history.copy()
        jisdor["trading_date"] = pd.to_datetime(jisdor["trading_date"])
        policy["effective_date"] = pd.to_datetime(policy["effective_date"])
        jisdor = jisdor.dropna(subset=["jisdor_rate"]).sort_values("trading_date")
        policy = policy.dropna(subset=["policy_rate"]).sort_values("effective_date")

        if jisdor.empty or policy.empty:
            st.warning("JISDOR or BI Rate data is not available in PostgreSQL.")
        else:
            latest_fx = jisdor.iloc[-1]
            previous_fx = jisdor.iloc[-2] if len(jisdor) > 1 else latest_fx
            fx_change = latest_fx["jisdor_rate"] - previous_fx["jisdor_rate"]
            fx_change_pct = (
                fx_change / previous_fx["jisdor_rate"] * 100
                if previous_fx["jisdor_rate"] else 0
            )
            latest_policy = policy.iloc[-1]

            # Colored KPI cards, consistent with the Market Overview page.
            kpis = [
                ("LATEST JISDOR", f"Rp {latest_fx['jisdor_rate']:,.2f}",
                 f"{fx_change:+,.2f} IDR ({fx_change_pct:+.3f}%)", "linear-gradient(120deg,#1D4ED8,#2563EB 55%,#60A5FA)", "#DBEAFE"),
                ("BI POLICY RATE", f"{latest_policy['policy_rate']:.2f}%",
                 f"Effective {latest_policy['effective_date']:%d %b %Y}", "linear-gradient(120deg,#6D28D9,#7C3AED 55%,#A78BFA)", "#EDE9FE"),
                ("JISDOR OBSERVATIONS", f"{len(jisdor):,}",
                 f"Since {jisdor['trading_date'].min():%d %b %Y}", "linear-gradient(120deg,#047857,#059669 55%,#34D399)", "#D1FAE5"),
                ("BI RATE DECISIONS", f"{len(policy):,}",
                 f"Since {policy['effective_date'].min():%d %b %Y}", "linear-gradient(120deg,#B45309,#D97706 55%,#FBBF24)", "#FEF3C7"),
            ]
            kcols = st.columns(4)
            for col, (label, value, detail, gradient, soft) in zip(kcols, kpis):
                with col:
                    st.markdown(textwrap.dedent(f"""
                        <div style="background:{gradient};padding:20px;border-radius:14px;
                            min-height:118px;box-shadow:0 5px 16px rgba(0,0,0,.12);
                            display:flex;flex-direction:column;justify-content:center;gap:8px;">
                            <div style="color:{soft};font-size:11px;font-weight:700;letter-spacing:1px;">{label}</div>
                            <div style="color:#FFFFFF;font-size:27px;font-weight:750;line-height:1.15;">{value}</div>
                            <div style="color:#FFFFFF;font-size:12px;font-weight:600;opacity:.95;">{detail}</div>
                        </div>
                    """), unsafe_allow_html=True)

            st.markdown("### USD/IDR Reference Rate — JISDOR")
            period = st.selectbox(
                "JISDOR display period",
                ["1 Year", "3 Years", "All Available Data"],
                index=1,
                key="macro_jisdor_period"
            )
            days = {"1 Year": 365, "3 Years": 1095, "All Available Data": None}[period]
            fx_plot = jisdor.copy()
            if days is not None:
                fx_plot = fx_plot[
                    fx_plot["trading_date"] >= (
                        fx_plot["trading_date"].max() - pd.Timedelta(days=days)
                    )
                ]

            fx_fig = go.Figure()
            fx_fig.add_trace(go.Scatter(
                x=fx_plot["trading_date"],
                y=fx_plot["jisdor_rate"],
                mode="lines",
                name="JISDOR",
                line=dict(color="#3478F6", width=2),
                hovertemplate="%{x|%d %b %Y}<br>Rp %{y:,.2f}<extra></extra>"
            ))
            fx_fig.update_layout(
                template="plotly_white",
                height=390,
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                yaxis_title="IDR per USD",
                xaxis_title="",
                margin=dict(l=20, r=20, t=20, b=20),
                hovermode="x unified",
                font=dict(family="Arial", size=12, color="#30343B"),
                xaxis=dict(
                    title=dict(font=dict(color="#30343B", size=12)),
                    tickfont=dict(color="#30343B", size=11),
                    showgrid=False, zeroline=False, showline=True,
                    linecolor="#9CA3AF", tickcolor="#6B7280"
                ),
                yaxis=dict(
                    title=dict(font=dict(color="#30343B", size=12)),
                    tickfont=dict(color="#30343B", size=11),
                    tickformat=",.0f", separatethousands=True,
                    gridcolor="#E5E7EB", zeroline=False,
                    showline=True, linecolor="#9CA3AF"
                )
            )
            st.plotly_chart(fx_fig, use_container_width=True)

            fx_plot["daily_change"] = fx_plot["jisdor_rate"].diff()
            change_fig = go.Figure(go.Bar(
                x=fx_plot["trading_date"],
                y=fx_plot["daily_change"],
                marker_color=[
                    "#E5484D" if value > 0 else "#159A75"
                    for value in fx_plot["daily_change"].fillna(0)
                ],
                name="Daily change",
                hovertemplate="%{x|%d %b %Y}<br>Change: %{y:+,.2f} IDR<extra></extra>"
            ))
            change_fig.update_layout(
                template="plotly_white",
                height=230,
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                yaxis_title="Daily change (IDR)",
                xaxis_title="",
                margin=dict(l=65, r=25, t=15, b=45),
                font=dict(family="Arial", size=12, color="#30343B"),
                xaxis=dict(
                    tickfont=dict(color="#30343B", size=11),
                    showgrid=False, zeroline=False, showline=True,
                    linecolor="#9CA3AF", tickcolor="#6B7280"
                ),
                yaxis=dict(
                    title=dict(font=dict(color="#30343B", size=12)),
                    tickfont=dict(color="#30343B", size=11),
                    tickformat="+,.0f", gridcolor="#E5E7EB",
                    zeroline=True, zerolinecolor="#6B7280",
                    showline=True, linecolor="#9CA3AF"
                )
            )
            st.plotly_chart(change_fig, use_container_width=True)
            st.caption(
                "A positive daily change means the rupiah weakened against the US dollar; "
                "a negative change means it strengthened. JISDOR is Bank Indonesia's "
                "USD/IDR reference rate."
            )

            st.divider()
            st.markdown("### Bank Indonesia Policy Rate")
            policy_fig = go.Figure(go.Scatter(
                x=policy["effective_date"],
                y=policy["policy_rate"],
                mode="lines+markers",
                line=dict(color="#8B5CF6", width=2, shape="hv"),
                marker=dict(size=5),
                name="BI Rate",
                hovertemplate="%{x|%d %b %Y}<br>BI Rate: %{y:.2f}%<extra></extra>"
            ))
            policy_fig.update_layout(
                template="plotly_white",
                height=340,
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                yaxis_title="Policy rate (%)",
                xaxis_title="",
                margin=dict(l=65, r=25, t=20, b=45),
                hovermode="x unified",
                font=dict(family="Arial", size=12, color="#30343B"),
                xaxis=dict(
                    tickfont=dict(color="#30343B", size=11),
                    showgrid=False, zeroline=False, showline=True,
                    linecolor="#9CA3AF", tickcolor="#6B7280"
                ),
                yaxis=dict(
                    title=dict(font=dict(color="#30343B", size=12)),
                    tickfont=dict(color="#30343B", size=11),
                    ticksuffix="%", gridcolor="#E5E7EB",
                    zeroline=False, showline=True, linecolor="#9CA3AF"
                )
            )
            st.plotly_chart(policy_fig, use_container_width=True)

            policy_display = policy.sort_values(
                "effective_date", ascending=False
            ).head(12).copy()
            policy_display["effective_date"] = policy_display["effective_date"].dt.strftime("%d %b %Y")
            policy_display.columns = ["Effective Date", "BI Rate (%)", "Source"]
            st.markdown("#### Latest Policy-Rate Decisions")
            policy_styled = (
                style_dark_table(policy_display)
                .format({"BI Rate (%)": "{:.2f}%"})
                .set_table_attributes(
                    'style="width:100%; min-width:100%; table-layout:auto;"'
                )
                .hide(axis="index")
            )
            st.html(policy_styled.to_html())

            st.markdown("### Data Notes")
            st.caption(
                "JISDOR is daily and reflects the USD/IDR reference rate. BI Rate is "
                "an event-based series: each observation represents an effective policy "
                "rate from its effective date, not a separate daily observation. "
                "Sources: Bank Indonesia."
            )

    # =====================================================
    # PAGE 7: PIPELINE INFORMATION
    # =====================================================

    elif page == "Pipeline Information":

        st.markdown(
            '<div class="section-label">DATA ENGINEERING MONITORING</div>',
            unsafe_allow_html=True
        )

        st.subheader("Pipeline Information")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Stocks Available",
            performance["symbol"].nunique()
        )

        col2.metric(
            "Latest Data Date",
            str(latest_date.date())
        )

        col3.metric(
            "Mart Records",
            len(performance)
        )

        st.markdown("### Data Source")

        st.write("Yahoo Finance via yfinance")

        st.markdown("### Data Warehouse")

        st.write("PostgreSQL 16")

        st.markdown("### Transformation Engine")

        st.write("dbt Core 1.12.6")

        st.markdown("### Data Pipeline")

        st.write(
            "Python Ingestion → Parquet Data Lake → "
            "PostgreSQL → dbt → Streamlit"
        )

        st.info(
            "This dashboard displays the latest data available "
            "in the local PostgreSQL warehouse. "
            "Pipeline freshness is not automatically monitored yet."
        )


except Exception as error:

    st.error("Unable to load dashboard data.")

    st.exception(error)

    st.info(
        "Check PostgreSQL connection, .env configuration "
        "and dbt models."
    )
git status