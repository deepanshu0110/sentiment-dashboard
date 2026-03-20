# 📈 Crypto Market Sentiment Dashboard

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red?style=flat-square&logo=streamlit)
![NLP](https://img.shields.io/badge/NLP-VADER-purple?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

Real-time dashboard analyzing cryptocurrency news & social media sentiment using FastAPI, Streamlit, and VADER Sentiment.

---

## 🚀 Features

- **FastAPI backend** → serves processed sentiment data (`/sentiment`, `/symbols`, `/summary`)
- **Streamlit dashboard** → interactive charts & live refresh
- **VADER Sentiment** → quick polarity scoring of crypto headlines
- **Auto data refresh** → headlines shifted to today's date for testing
- **Multiple coins** → BTC, ETH included by default (easy to extend)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Dashboard UI | Streamlit |
| Sentiment Engine | VADER Sentiment |
| Visualization | Plotly |
| Data Processing | Pandas |

---

## 📂 Project Structure

```
sentiment-dashboard/
├── api/
│   └── sentiment_api.py      # FastAPI backend
├── app/
│   └── dashboard.py          # Streamlit frontend
├── data/
│   ├── sample_headlines.csv  # Seed headlines (in repo)
│   └── sentiment.csv         # Generated at runtime (gitignored)
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚡ Quickstart

### 1️⃣ Clone & install
```bash
git clone https://github.com/deepanshu0110/sentiment-dashboard.git
cd sentiment-dashboard
pip install -r requirements.txt
```

### 2️⃣ Run the API
```bash
uvicorn api.sentiment_api:app --reload --port 8000
```
API: http://localhost:8000 | Swagger: http://localhost:8000/docs

### 3️⃣ Run the Dashboard
```bash
streamlit run app/dashboard.py --server.port 8501
```
Dashboard: http://localhost:8501

---

## 🔑 API Endpoints

| Endpoint | Description |
|---|---|
| `GET /health` | API health + record count |
| `GET /symbols` | Available coins (BTC, ETH) |
| `GET /sentiment?symbol=BTC&window=60` | Sentiment data (last 60 min) |
| `GET /sentiment/summary` | Overall market sentiment |

---

## 🧩 Roadmap

- [x] BTC & ETH demo with sample data
- [ ] Add more coins (SOL, BNB, XRP)
- [ ] Live news API integration (NewsAPI / CryptoPanic)
- [ ] WebSocket real-time updates
- [ ] Docker deployment

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
