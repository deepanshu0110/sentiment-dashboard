"""
Market Sentiment Analysis Dashboard
Interactive Streamlit dashboard for cryptocurrency sentiment tracking
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# ──────────────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Sentiment Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
API_BASE_URL = "http://localhost:8000"
DEFAULT_SYMBOLS = ["BTC", "ETH"]
TIME_WINDOWS = {
    "30 minutes": 30,
    "1 hour": 60,
    "2 hours": 120,
    "4 hours": 240,
    "12 hours": 720,
    "24 hours": 1440,
}

# ──────────────────────────────────────────────────────────────────────────────
# Styles
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
.main > div { padding-top: 1rem; }
.block-container { padding-top: 1.5rem; }
.api-ok { background: rgba(0, 180, 80, .12); border: 1px solid rgba(0,180,80,.4);
          padding: .6rem .8rem; border-radius: 8px; }
.api-bad { background: rgba(220, 30, 30, .12); border: 1px solid rgba(220,30,30,.4);
           padding: .6rem .8rem; border-radius: 8px; }
</style>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# API helpers
# ──────────────────────────────────────────────────────────────────────────────
def api_get(path: str, params: dict | None = None, timeout: int = 10):
    url = f"{API_BASE_URL}{path}"
    return requests.get(url, params=params, timeout=timeout)

def check_api_health() -> dict | None:
    try:
        r = api_get("/health", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def get_available_symbols() -> list[str]:
    try:
        r = api_get("/symbols", timeout=10)
        if r.status_code == 200:
            syms = r.json().get("symbols", [])
            return syms if syms else DEFAULT_SYMBOLS
    except Exception:
        pass
    return DEFAULT_SYMBOLS

def get_sentiment(symbol: str, window: int) -> dict | None:
    try:
        r = api_get("/sentiment", params={"symbol": symbol, "window": window}, timeout=10)
        if r.status_code == 200:
            return r.json()
        st.error(f"API Error fetching /sentiment: HTTP {r.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("🚨 Cannot connect to API at http://localhost:8000")
    except requests.exceptions.Timeout:
        st.error("⏱️ API request timed out.")
    except Exception as e:
        st.error(f"❌ Error: {e}")
    return None

def get_summary() -> dict | None:
    try:
        r = api_get("/sentiment/summary", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

# ──────────────────────────────────────────────────────────────────────────────
# Viz helpers
# ──────────────────────────────────────────────────────────────────────────────
def sentiment_color_emoji(score: float) -> str:
    if score > 0.05: return "🟢"
    if score < -0.05: return "🔴"
    return "🟡"

def timeline_chart(data: dict):
    if not data or not data.get("timeline"):
        return None
    df = pd.DataFrame(data["timeline"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["sentiment_score"],
        mode="lines+markers",
        name="Sentiment Score",
        line=dict(width=3),
        marker=dict(size=8),
        hovertemplate="<b>%{y:.3f}</b><br>%{x}<extra></extra>"
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=0.05, line_dash="dot", line_color="green", opacity=0.3)
    fig.add_hline(y=-0.05, line_dash="dot", line_color="red", opacity=0.3)
    fig.update_layout(
        title=f"Sentiment Timeline — {data['symbol']}",
        height=420,
        xaxis_title="Time",
        yaxis_title="Sentiment Score",
        hovermode="x unified",
        showlegend=True,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig

def distribution_chart(data: dict):
    if not data or not data.get("timeline"):
        return None
    df = pd.DataFrame(data["timeline"])
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df["sentiment_score"], nbinsx=20, name="Scores"))
    fig.update_layout(
        title="Sentiment Score Distribution",
        height=320,
        xaxis_title="Sentiment Score",
        yaxis_title="Frequency",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig

def recent_headlines(data: dict, limit: int = 6):
    if not data or not data.get("timeline"):
        st.info("No headlines available in this window.")
        return
    items = sorted(data["timeline"], key=lambda x: x["timestamp"], reverse=True)[:limit]
    for h in items:
        score = float(h["sentiment_score"])
        emoji = sentiment_color_emoji(score)
        with st.expander(f"{emoji} {h['headline'][:90]}…"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"**Headline:** {h['headline']}")
                st.write(f"**Source:** {h['source']}")
                st.write(f"**Time:** {pd.to_datetime(h['timestamp']).strftime('%H:%M:%S')}")
            with c2:
                label = "Positive" if score > 0.05 else "Negative" if score < -0.05 else "Neutral"
                st.metric("Sentiment", f"{score:.3f}", label)

# ──────────────────────────────────────────────────────────────────────────────
# Main app
# ──────────────────────────────────────────────────────────────────────────────
def main():
    # Title
    st.title("📈 Crypto Market Sentiment Dashboard")
    st.caption("Real-time sentiment analysis of cryptocurrency news and social media")

    # API status banner
    health = check_api_health()
    if health and health.get("data_status") == "OK":
        st.markdown(
            f'<div class="api-ok">✅ API connected · '
            f'{health.get("records", 0)} records · '
            f'Last check: {datetime.now().strftime("%H:%M:%S")}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="api-bad">🚨 API not responding. '
            'Start it with: <code>uvicorn api.sentiment_api:app --reload --port 8000</code></div>',
            unsafe_allow_html=True,
        )
        st.stop()

    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Controls")
        symbols = get_available_symbols()
        symbol = st.selectbox("📊 Select Cryptocurrency", symbols, index=0)

        window_label = st.selectbox("⏱️ Time Window", list(TIME_WINDOWS.keys()), index=1)
        window = TIME_WINDOWS[window_label]

        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=True)
        if st.button("🔄 Refresh Now", type="primary"):
            st.rerun()

        st.markdown("---")
        st.write("**API:**", API_BASE_URL)

    # Fetch selected sentiment
    with st.spinner("Fetching sentiment data…"):
        data = get_sentiment(symbol, window)

    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    if data:
        summary = data.get("summary", {})
        with c1:
            st.metric("Average Sentiment",
                      f"{summary.get('avg_sentiment', 0):.3f}",
                      summary.get("sentiment_label", "Neutral"))
        with c2:
            st.metric("Total Headlines", summary.get("total_headlines", 0), f"Last {window_label}")
        with c3:
            st.metric("Data Points", data.get("data_points", 0), symbol)
        with c4:
            st.metric("Time Range", summary.get("time_range", "N/A"), "Latest")
    else:
        st.warning("No sentiment data returned for this selection.")

    st.markdown("---")

    # Charts
    cc1, cc2 = st.columns([2, 1])
    with cc1:
        fig_t = timeline_chart(data)
        if fig_t:
            st.plotly_chart(fig_t, use_container_width=True)
        else:
            st.info("No timeline data for the chosen window.")
    with cc2:
        fig_d = distribution_chart(data)
        if fig_d:
            st.plotly_chart(fig_d, use_container_width=True)

    # Headlines
    st.markdown("---")
    st.subheader("📰 Recent Headlines")
    recent_headlines(data, limit=6)

    # Overall summary
    st.markdown("---")
    st.subheader("📊 Overall Market Sentiment")
    overall = get_summary()
    if overall and overall.get("summary"):
        sdf = pd.DataFrame(overall["summary"]).T
        sdf = sdf.round(3)
        cols = st.columns(max(1, len(sdf)))
        for i, (sym, row) in enumerate(sdf.iterrows()):
            with cols[i]:
                st.metric(f"{sentiment_color_emoji(row['avg_sentiment'])} {sym}",
                          f"{row['avg_sentiment']:.3f}",
                          row["sentiment_label"])

    # Footer
    st.markdown("---")
    fc1, fc2, fc3 = st.columns(3)
    with fc1: st.caption("Last Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    with fc2: st.caption("Data Source: News Headlines + VADER Sentiment")
    with fc3: st.caption("Refresh: Auto 30s" if auto_refresh else "Refresh: Manual")

    if auto_refresh:
        time.sleep(30)
        st.rerun()

# ── run app (call unconditionally so Streamlit renders) ───────────────────────
main()
