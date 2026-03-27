# Crypto Sentiment Dashboard

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red?style=flat-square&logo=streamlit)
![NLP](https://img.shields.io/badge/NLP-VADER-purple?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

Analyzes crypto news headlines in real time, scores sentiment using VADER, and displays live polarity trends via a Streamlit dashboard backed by FastAPI.

---

## Business Problem

Crypto prices move on sentiment. Traders and analysts need a fast signal on whether market chatter is bullish or bearish — without reading hundreds of headlines manually.

---

## Architecture

```
Headlines → VADER Scoring → FastAPI → Streamlit Dashboard
```

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /health` | Status + record count |
| `GET /symbols` | Available coins |
| `GET /sentiment?symbol=BTC&window=60` | Last 60-min sentiment |
| `GET /sentiment/summary` | Overall market polarity |

---

## Quickstart

```bash
git clone https://github.com/deepanshu0110/sentiment-dashboard.git
cd sentiment-dashboard
pip install -r requirements.txt
uvicorn api.sentiment_api:app --reload --port 8000   # Terminal 1
streamlit run app/dashboard.py --server.port 8501    # Terminal 2
```

---

## Tech Stack

Python · VADER Sentiment · FastAPI · Streamlit · Plotly · Pandas

---

## Roadmap

- [ ] Live NewsAPI / CryptoPanic integration
- [ ] WebSocket real-time push
- [ ] Expand to SOL, BNB, XRP
- [ ] Docker deployment

---

## Author

**Deepanshu Garg** — Freelance Data Scientist
- GitHub: [@deepanshu0110](https://github.com/deepanshu0110)
- Hire: [freelancer.com/u/deepanshu0110](https://www.freelancer.com/u/deepanshu0110)

MIT License