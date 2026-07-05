"""QVeris client tests: initialization, missing-key behavior, mock fallback,
and response normalization."""

import pytest

from app.config import Settings
from app.schemas.qveris import MarketDataBundle
from app.services.market_data_service import MarketDataService
from app.services.qveris_client import QverisClient, QverisNotConfiguredError


def make_settings(**overrides) -> Settings:
    s = Settings()
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


class TestQverisClientInit:
    def test_unconfigured_without_key(self):
        client = QverisClient(make_settings(qveris_api_key=""))
        assert client.is_configured is False

    def test_configured_with_key(self):
        client = QverisClient(make_settings(qveris_api_key="test-key-not-real"))
        assert client.is_configured is True
        assert client.base_url.startswith("https://qveris.ai")
        assert client.session_id == "alphainvestpro-local"

    def test_missing_key_raises_on_call(self):
        client = QverisClient(make_settings(qveris_api_key=""))
        with pytest.raises(QverisNotConfiguredError):
            client.discover()
        with pytest.raises(QverisNotConfiguredError):
            client.call("any.capability", {})


class TestMockFallback:
    def test_bundle_falls_back_to_mock(self):
        service = MarketDataService(QverisClient(make_settings(qveris_api_key="")))
        bundle = service.get_bundle("AAPL")
        assert isinstance(bundle, MarketDataBundle)
        assert bundle.is_mock is True
        assert bundle.quote.meta.is_mock is True
        assert "MOCK DATA" in bundle.quote.meta.quality_notes

    def test_unknown_ticker_gets_generic_mock(self):
        service = MarketDataService(QverisClient(make_settings(qveris_api_key="")))
        bundle = service.get_bundle("ZZZZ")
        assert bundle.is_mock is True
        assert "ZZZZ" in bundle.profile.name

    def test_status_reports_mock_mode(self):
        service = MarketDataService(QverisClient(make_settings(qveris_api_key="")))
        status = service.status()
        assert status.configured is False
        assert status.mode == "mock"


class TestNormalization:
    def test_quote_normalization_from_raw_response(self):
        service = MarketDataService(QverisClient(make_settings(qveris_api_key="k")))
        raw = {
            "provider": "demo-provider",
            "data": {"price": 123.45, "change_percent": 1.2, "volume": 1000,
                     "market_cap": 5e9, "currency": "USD", "timestamp": "2026-07-01T00:00:00Z"},
        }
        quote = service._normalize_quote("TEST", raw, "cap.quote")
        assert quote.price == 123.45
        assert quote.symbol == "TEST"
        assert quote.meta.capability_id == "cap.quote"
        assert quote.meta.provider == "demo-provider"
        assert quote.meta.source_timestamp == "2026-07-01T00:00:00Z"
        assert quote.meta.retrieval_timestamp  # always recorded

    def test_every_mock_datapoint_has_provenance(self):
        service = MarketDataService(QverisClient(make_settings(qveris_api_key="")))
        bundle = service.get_bundle("MSFT")
        for obj in (bundle.quote, bundle.profile, bundle.fundamentals, bundle.news):
            assert obj.meta.retrieval_timestamp
            assert obj.meta.symbol == "MSFT"
            assert obj.meta.provider in ("mock", "qveris")
