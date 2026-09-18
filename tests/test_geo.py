import json
import io
import urllib.request
import pytest
from tcalm_core.geo import detect_location
from tcalm_core.constants import DEFAULT_CONFIG


class MockResponse:
    def __init__(self, data):
        self.data = json.dumps(data).encode("utf-8")

    def read(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def test_detect_location_ip_api_success(monkeypatch):
    sample_data = {
        "status": "success",
        "city": "Cairo",
        "country": "Egypt",
        "lat": 30.0444,
        "lon": 31.2357,
        "timezone": "Africa/Cairo",
    }

    def mock_urlopen(req, timeout=4):
        return MockResponse(sample_data)

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    cfg = detect_location()
    assert cfg["city"] == "Cairo"
    assert cfg["country"] == "Egypt"
    assert cfg["method"] == 5
    assert cfg["auto_detect"] is True


def test_detect_location_method_selection(monkeypatch):
    countries_methods = [
        ("Saudi Arabia", 4),
        ("United Arab Emirates", 8),
        ("Turkey", 13),
        ("Pakistan", 1),
        ("United States", 2),
        ("United Kingdom", 3),
    ]

    for country, expected_method in countries_methods:
        sample_data = {
            "status": "success",
            "city": "Capital",
            "country": country,
            "lat": 25.0,
            "lon": 45.0,
            "timezone": "UTC",
        }

        def mock_urlopen(req, timeout=4):
            return MockResponse(sample_data)

        monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
        cfg = detect_location()
        assert cfg["method"] == expected_method, f"Failed for {country}"


def test_detect_location_network_error(monkeypatch):
    def mock_urlopen_fail(req, timeout=4):
        raise urllib.error.URLError("Network unreachable")

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen_fail)

    cfg = detect_location()
    # Should fallback gracefully without raising an unhandled exception
    assert "city" in cfg
    assert "country" in cfg
