📈 Crypto Market Sentiment Dashboard

Real-time dashboard that analyzes cryptocurrency news & social media sentiment using FastAPI, Streamlit, and VADER Sentiment.

🚀 Features

FastAPI backend → serves processed sentiment data (/sentiment, /symbols, /summary)

Streamlit dashboard → interactive charts & live refresh

VADER Sentiment → quick polarity scoring of crypto headlines

Auto data refresh → headlines automatically shifted to today’s date for testing

Multiple coins → BTC, ETH included by default (easy to extend)

🛠️ Tech Stack

FastAPI
 – backend API

Streamlit
 – dashboard UI

VADER Sentiment
 – sentiment scoring

Plotly
 – charts & visualizations

Pandas
 – data wrangling

📂 Project Structure
sentiment-dashboard/
│
├── api/
│   └── sentiment_api.py      # FastAPI backend
│
├── app/
│   └── dashboard.py          # Streamlit frontend
│
├── data/
│   ├── sample_headlines.csv  # Seed sample headlines (kept in repo)
│   └── sentiment.csv         # Generated at runtime (ignored by git)
│
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── .gitignore

⚡ Quickstart
1️⃣ Clone & install
git clone https://github.com/<your-username>/sentiment-dashboard.git
cd sentiment-dashboard
pip install -r requirements.txt

2️⃣ Run the API
uvicorn api.sentiment_api:app --reload --port 8000


API runs at http://localhost:8000

Interactive docs: http://localhost:8000/docs

3️⃣ Run the Dashboard
streamlit run app/dashboard.py --server.port 8501


Dashboard at http://localhost:8501

🔑 Example Endpoints

GET /health → API health + records count

GET /symbols → available coins (BTC, ETH)

GET /sentiment?symbol=BTC&window=60 → sentiment data (last 60 min)

GET /sentiment/summary → overall market sentiment

📊 Dashboard Preview

Select cryptocurrency (BTC / ETH)

Choose a time window (30 min → 24 hours)

View:

Sentiment timeline (line chart)

Sentiment distribution (histogram)

Recent headlines

Overall market sentiment summary

🧩 Roadmap

✅ BTC & ETH demo with sample data

🔄 Add more coins (SOL, BNB…)

🔌 Connect to live news API (CryptoPanic, NewsAPI, Twitter/X)

📦 Deploy on Streamlit Cloud / Render / Railway