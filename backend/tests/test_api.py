"""API endpoint tests via FastAPI TestClient."""

import time

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _wait_for_completion(job_id: str, timeout: float = 20.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        job = client.get(f"/api/analysis-jobs/{job_id}").json()
        if job["status"] in ("completed", "failed"):
            return job
        time.sleep(0.2)
    raise AssertionError("job did not finish in time")


class TestHealthAndStatus:
    def test_health(self):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["research_only"] is True

    def test_qveris_status_mock_mode(self):
        resp = client.get("/api/market-data/qveris/status")
        assert resp.status_code == 200
        assert resp.json()["mode"] == "mock"

    def test_qveris_sources_mock(self):
        resp = client.get("/api/market-data/qveris/sources")
        assert resp.status_code == 200
        assert any("MOCK DATA" in s["description"] for s in resp.json()["sources"])

    def test_qveris_fetch(self):
        resp = client.post("/api/market-data/qveris/fetch", json={"ticker": "AAPL"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["is_mock"] is True
        assert body["quote"]["price"] > 0

    def test_settings_never_expose_keys(self):
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        text = resp.text.lower()
        assert "api_key" not in text
        body = resp.json()
        assert body["deepseek"]["model"] == "deepseek-chat"
        assert set(body["deepseek"].keys()) == {"configured", "model", "mode"}


class TestAnalysisJobFlow:
    def test_create_and_complete_job(self):
        resp = client.post(
            "/api/analysis-jobs",
            json={"ticker": "aapl", "analysis_mode": "full_memo", "language": "en"},
        )
        assert resp.status_code == 201
        job = resp.json()
        assert job["ticker"] == "AAPL"
        finished = _wait_for_completion(job["id"])
        assert finished["status"] == "completed"
        assert finished["report_id"]

        report = client.get(f"/api/analysis-jobs/{job['id']}/report")
        assert report.status_code == 200
        data = report.json()["report"]
        assert data["final_verdict"] in ("avoid", "watchlist", "attractive", "uncertain")
        assert data["is_mock_data"] is True

    def test_invalid_mode_rejected(self):
        resp = client.post("/api/analysis-jobs", json={"ticker": "AAPL", "analysis_mode": "live_trading"})
        assert resp.status_code == 422

    def test_missing_job_404(self):
        assert client.get("/api/analysis-jobs/nope").status_code == 404

    def test_reports_listing(self):
        resp = client.get("/api/reports")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestWatchlist:
    def test_watchlist_crud(self):
        created = client.post("/api/watchlist", json={"ticker": "ko", "note": "quality compounder"})
        assert created.status_code == 201
        item = created.json()
        assert item["ticker"] == "KO"

        listed = client.get("/api/watchlist").json()
        assert any(i["id"] == item["id"] for i in listed)

        deleted = client.delete(f"/api/watchlist/{item['id']}")
        assert deleted.status_code == 204
        assert not any(i["id"] == item["id"] for i in client.get("/api/watchlist").json())


class TestSettingsUpdate:
    def test_update_language_setting(self):
        resp = client.put("/api/settings", json={"values": {"default_language": "zh-CN"}})
        assert resp.status_code == 200
        assert resp.json()["values"]["default_language"] == "zh-CN"
