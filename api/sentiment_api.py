"""
Market Sentiment Analysis API
Analyzes cryptocurrency news headlines and provides sentiment scores
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from datetime import datetime, timedelta, date
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# -------------------------------
# Initialize
# -------------------------------
app = FastAPI(
    title="Market Sentiment API",
    description="API for cryptocurrency market sentiment analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = SentimentIntensityAnalyzer()
headlines_df = None
sentiment_df = None
DEFAULT_SYMBOLS = ["BTC", "ETH"]

# -------------------------------
# Helpers
# -------------------------------
def _make_fresh_sample_df(now=None):
    """Generate some sample data with recent timestamps."""
    if now is None:
        now = datetime.now()
    base = now.replace(second=0, microsecond=0)
    rows = [
        (base - timedelta(minutes=90), "BTC", "Bitcoin surges past $63000 as institutional adoption accelerates", "CryptoNews"),
        (base - timedelta(minutes=75), "BTC", "Major bank announces Bitcoin custody services for wealthy clients", "FinancialTimes"),
        (base - timedelta(minutes=60), "ETH", "Ethereum network upgrade reduces transaction fees by 40%", "CoinDesk"),
        (base - timedelta(minutes=45), "BTC", "Regulatory clarity boosts Bitcoin sentiment among investors", "Reuters"),
        (base - timedelta(minutes=30), "ETH", "DeFi protocols see massive inflows as Ethereum prices stabilize", "CryptoDaily"),
        (base - timedelta(minutes=15), "BTC", "Bitcoin mining difficulty adjusts downward helping smaller miners", "BitcoinMagazine"),
        (base,                        "ETH", "Ethereum developers announce successful testnet for next upgrade", "EthereumFoundation"),
    ]
    return pd.DataFrame(rows, columns=["timestamp", "symbol", "headline", "source"])

def _shift_df_to_today(df: pd.DataFrame, ts_col="timestamp") -> pd.DataFrame:
    """Shift all timestamps to today’s date (keep HH:MM:SS)."""
    df = df.copy()
    df[ts_col] = pd.to_datetime(df[ts_col])
    today = date.today()
    df[ts_col] = df[ts_col].apply(lambda t: t.replace(year=today.year, month=today.month, day=today.day))
    return df

def _ensure_fresh_headlines(headlines_path: str) -> pd.DataFrame:
    """Ensure headlines CSV exists, valid, and shifted to today."""
    expected_cols = {"timestamp", "symbol", "headline", "source"}

    # If missing → create fresh
    if (not os.path.exists(headlines_path)) or os.path.getsize(headlines_path) == 0:
        print(f"Creating sample data at {headlines_path}")
        df = _make_fresh_sample_df()
        df.to_csv(headlines_path, index=False)
        return df

    # Load
    df = pd.read_csv(headlines_path)
    if df.empty or not expected_cols.issubset(df.columns):
        print("Headlines file empty or malformed. Rebuilding sample.")
        df = _make_fresh_sample_df()
        df.to_csv(headlines_path, index=False)
        return df

    # Shift to today
    df = _shift_df_to_today(df, "timestamp")
    df.to_csv(headlines_path, index=False)
    return df

def process_sentiment_analysis():
    """Run sentiment analysis on headlines_df and save to CSV."""
    global headlines_df, sentiment_df
    if headlines_df is None or headlines_df.empty:
        return
    results = []
    for _, row in headlines_df.iterrows():
        scores = analyzer.polarity_scores(str(row["headline"]))
        results.append({
            "timestamp": row["timestamp"],
            "symbol": str(row["symbol"]).upper(),
            "headline": row["headline"],
            "compound": scores["compound"],
            "positive": scores["pos"],
            "negative": scores["neg"],
            "neutral": scores["neu"],
            "source": row["source"],
        })
    sentiment = pd.DataFrame(results)
    os.makedirs("data", exist_ok=True)
    sentiment.to_csv("data/sentiment.csv", index=False)
    sentiment["timestamp"] = pd.to_datetime(sentiment["timestamp"])
    sentiment.sort_values("timestamp", inplace=True)
    sentiment.reset_index(drop=True, inplace=True)
    globals()["sentiment_df"] = sentiment
    print(f"Processed and saved {len(sentiment)} sentiment records")

def load_and_process_data():
    """Load headlines and sentiment, repairing if needed."""
    global headlines_df, sentiment_df
    try:
        os.makedirs("data", exist_ok=True)
        headlines_path = os.path.join("data", "sample_headlines.csv")
        sentiment_path = os.path.join("data", "sentiment.csv")

        # Ensure headlines exist + fresh timestamps
        headlines_df_local = _ensure_fresh_headlines(headlines_path)
        headlines_df_local["timestamp"] = pd.to_datetime(headlines_df_local["timestamp"])
        headlines_df_local["symbol"] = headlines_df_local["symbol"].astype(str).str.upper()
        headlines_df_local.sort_values("timestamp", inplace=True)
        headlines_df_local.reset_index(drop=True, inplace=True)
        globals()["headlines_df"] = headlines_df_local

        # Load or build sentiment
        if os.path.exists(sentiment_path) and os.path.getsize(sentiment_path) > 0:
            s = pd.read_csv(sentiment_path)
            valid = (not s.empty) and {"timestamp","symbol","headline","compound"}.issubset(s.columns)
            if valid:
                s["timestamp"] = pd.to_datetime(s["timestamp"])
                s.sort_values("timestamp", inplace=True)
                s.reset_index(drop=True, inplace=True)
                globals()["sentiment_df"] = s
                print(f"Loaded existing sentiment data: {len(s)} records")
            else:
                print("Existing sentiment.csv invalid. Reprocessing.")
                process_sentiment_analysis()
        else:
            print("Processing sentiment analysis...")
            process_sentiment_analysis()
        return True
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return False

def filter_sentiment_data(symbol: str, window_minutes: int) -> pd.DataFrame:
    if sentiment_df is None or sentiment_df.empty:
        return pd.DataFrame()
    now = datetime.now()
    cutoff = now - timedelta(minutes=window_minutes)
    df = sentiment_df[
        (sentiment_df["symbol"].str.upper() == symbol.upper()) &
        (sentiment_df["timestamp"] >= cutoff)
    ].copy()
    return df.sort_values("timestamp")

def get_sentiment_label(score: float) -> str:
    if score >= 0.05: return "Positive"
    if score <= -0.05: return "Negative"
    return "Neutral"

# -------------------------------
# Startup
# -------------------------------
@app.on_event("startup")
async def startup_event():
    ok = load_and_process_data()
    if ok:
        print("✅ API initialized successfully")
    else:
        print("⚠️ Warning: Could not load all data")

# -------------------------------
# Endpoints
# -------------------------------
@app.get("/")
async def root():
    return {
        "message": "Market Sentiment Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "sentiment": "/sentiment?symbol=BTC&window=60",
            "symbols": "/symbols",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    count = len(sentiment_df) if sentiment_df is not None else 0
    return {
        "status": "healthy",
        "data_status": "OK" if count > 0 else "No Data",
        "records": count,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/symbols")
async def get_symbols():
    if sentiment_df is None or sentiment_df.empty:
        return {"symbols": DEFAULT_SYMBOLS}
    symbols = sorted(sentiment_df["symbol"].dropna().unique().tolist())
    return {"symbols": symbols if symbols else DEFAULT_SYMBOLS}

@app.get("/sentiment")
async def get_sentiment(
    symbol: str = Query(..., description="Cryptocurrency symbol (e.g., BTC, ETH)"),
    window: int = Query(60, ge=1, le=1440, description="Time window in minutes (1-1440)")
):
    if sentiment_df is None or sentiment_df.empty:
        raise HTTPException(status_code=503, detail="Sentiment data not available")
    filtered = filter_sentiment_data(symbol, window)
    if filtered.empty:
        return {
            "symbol": symbol.upper(),
            "window_minutes": window,
            "data_points": 0,
            "timeline": [],
            "summary": {
                "avg_sentiment": 0,
                "total_headlines": 0,
                "time_range": f"No data available for {symbol.upper()}",
                "sentiment_label": "Neutral"
            }
        }
    timeline = [{
        "timestamp": row["timestamp"].isoformat(),
        "sentiment_score": float(row["compound"]),
        "positive": float(row["positive"]),
        "negative": float(row["negative"]),
        "neutral": float(row["neutral"]),
        "headline": row["headline"],
        "source": row["source"]
    } for _, row in filtered.iterrows()]
    avg = float(filtered["compound"].mean())
    return {
        "symbol": symbol.upper(),
        "window_minutes": window,
        "data_points": len(filtered),
        "timeline": timeline,
        "summary": {
            "avg_sentiment": round(avg, 3),
            "total_headlines": len(filtered),
            "time_range": f"{filtered['timestamp'].min().strftime('%H:%M')} - {filtered['timestamp'].max().strftime('%H:%M')}",
            "sentiment_label": get_sentiment_label(avg)
        }
    }

@app.get("/sentiment/summary")
async def sentiment_summary():
    if sentiment_df is None or sentiment_df.empty:
        raise HTTPException(status_code=503, detail="Sentiment data not available")
    summary = {}
    for sym in sentiment_df["symbol"].unique():
        df = sentiment_df[sentiment_df["symbol"] == sym]
        avg = float(df["compound"].mean())
        summary[sym] = {
            "avg_sentiment": avg,
            "total_headlines": len(df),
            "latest_timestamp": df["timestamp"].max().isoformat(),
            "sentiment_label": get_sentiment_label(avg)
        }
    return {
        "summary": summary,
        "total_records": len(sentiment_df),
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
