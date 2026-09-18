import re
import json
import urllib.request
from datetime import date, datetime
import pytest
from tcalm_core.prayer import (
    calculate_offline_prayer_times,
    get_prayer_times,
)
from tcalm_core.constants import DEFAULT_CONFIG


def test_calculate_offline_prayer_times():
    # Cairo coordinates: 30.0444, 31.2357, UTC+2
    timings = calculate_offline_prayer_times(
        lat=30.0444,
        lng=31.2357,
        tz_offset=2.0,
        calc_date=date(2026, 9, 18),
        method=5
    )

    required_prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    time_regex = re.compile(r"^\d{2}:\d{2}$")

    for prayer in required_prayers:
        assert prayer in timings
        assert time_regex.match(timings[prayer]), f"Invalid format for {prayer}: {timings[prayer]}"

    # Chronological order check
    fajr = datetime.strptime(timings["Fajr"], "%H:%M")
    dhuhr = datetime.strptime(timings["Dhuhr"], "%H:%M")
    asr = datetime.strptime(timings["Asr"], "%H:%M")
    maghrib = datetime.strptime(timings["Maghrib"], "%H:%M")
    isha = datetime.strptime(timings["Isha"], "%H:%M")

    assert fajr < dhuhr < asr < maghrib < isha


def test_get_prayer_times_from_cache(isolated_tcalm_env):
    cache_file = isolated_tcalm_env["cache_file"]
    target_date = date(2026, 9, 18)
    date_str = target_date.strftime("%d-%m-%Y")
    cache_key = f"{date_str}_Cairo_Egypt_5"

    cached_data = {
        cache_key: {
            "Fajr": "04:15",
            "Dhuhr": "11:50",
            "Asr": "15:20",
            "Maghrib": "18:00",
            "Isha": "19:15"
        }
    }
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cached_data, f)

    cfg = {
        "city": "Cairo",
        "country": "Egypt",
        "method": 5,
        "latitude": 30.0444,
        "longitude": 31.2357
    }

    result = get_prayer_times(cfg, target_date=target_date)
    assert result["Fajr"] == "04:15"
    assert result["Maghrib"] == "18:00"


def test_get_prayer_times_api_success(monkeypatch, isolated_tcalm_env):
    target_date = date(2026, 9, 18)
    api_response = {
        "code": 200,
        "data": {
            "timings": {
                "Fajr": "04:18 (EEST)",
                "Dhuhr": "11:51 (EEST)",
                "Asr": "15:18 (EEST)",
                "Maghrib": "17:54 (EEST)",
                "Isha": "19:10 (EEST)"
            }
        }
    }

    class MockResponse:
        def read(self):
            return json.dumps(api_response).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=5: MockResponse())

    cfg = {
        "city": "Cairo",
        "country": "Egypt",
        "method": 5,
        "latitude": 30.0444,
        "longitude": 31.2357
    }

    result = get_prayer_times(cfg, target_date=target_date)
    assert result["Fajr"] == "04:18"
    assert result["Isha"] == "19:10"


def test_get_prayer_times_offline_fallback(monkeypatch, isolated_tcalm_env):
    def mock_urlopen_fail(req, timeout=5):
        raise urllib.error.URLError("No connection")

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen_fail)

    cfg = {
        "city": "Cairo",
        "country": "Egypt",
        "method": 5,
        "latitude": 30.0444,
        "longitude": 31.2357
    }

    result = get_prayer_times(cfg, target_date=date(2026, 9, 18))
    assert "Fajr" in result
    assert "Dhuhr" in result
    assert "Asr" in result
    assert "Maghrib" in result
    assert "Isha" in result
