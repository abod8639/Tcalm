import pytest
from tcalm_core.constants import (
    VERSION,
    CALCULATION_METHODS,
    PRAYER_NAMES_AR,
    DEFAULT_CONFIG,
)


def test_version():
    assert isinstance(VERSION, str)
    assert len(VERSION.split(".")) >= 3


def test_calculation_methods():
    assert isinstance(CALCULATION_METHODS, dict)
    assert 5 in CALCULATION_METHODS
    assert "Egyptian" in CALCULATION_METHODS[5]
    assert 4 in CALCULATION_METHODS
    assert "Umm Al-Qura" in CALCULATION_METHODS[4]


def test_prayer_names_ar():
    assert isinstance(PRAYER_NAMES_AR, dict)
    for prayer in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
        assert prayer in PRAYER_NAMES_AR
        assert isinstance(PRAYER_NAMES_AR[prayer], str)


def test_default_config_structure():
    required_keys = [
        "language",
        "auto_detect",
        "city",
        "country",
        "latitude",
        "longitude",
        "timezone",
        "method",
        "pause_duration_minutes",
        "pause_before_minutes",
        "notifications",
        "prayers",
    ]
    for key in required_keys:
        assert key in DEFAULT_CONFIG
    assert DEFAULT_CONFIG["pause_before_minutes"] == 1
    assert len(DEFAULT_CONFIG["prayers"]) == 5
