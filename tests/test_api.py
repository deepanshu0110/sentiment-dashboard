import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api"))


def test_sentiment_endpoints(monkeypatch):
    from fastapi.testclient import TestClient

    monkeypatch.chdir(ROOT)
    import sentiment_api

    with TestClient(sentiment_api.app) as client:
        health = client.get("/health").json()
        assert health["records"] > 0
        assert set(client.get("/symbols").json()["symbols"]) >= {"BTC", "ETH"}
        summary = client.get("/sentiment/summary").json()["summary"]
        assert -1 <= summary["BTC"]["avg_sentiment"] <= 1
        window = client.get("/sentiment", params={"symbol": "BTC", "window": 1440})
        assert window.status_code == 200
