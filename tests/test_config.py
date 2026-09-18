import os
import json
import pytest
from tcalm_core.config import (
    ensure_config_dir,
    log_message,
    load_config,
    save_config,
)
import tcalm_core.constants as consts


def test_ensure_config_dir(isolated_tcalm_env):
    config_dir = isolated_tcalm_env["config_dir"]
    assert os.path.exists(config_dir)


def test_log_message(isolated_tcalm_env):
    log_file = isolated_tcalm_env["log_file"]
    log_message("Test message 123")
    assert os.path.exists(log_file)
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Test message 123" in content


def test_save_and_load_config(isolated_tcalm_env):
    config_file = isolated_tcalm_env["config_file"]
    custom_cfg = {
        "language": "ar",
        "city": "Riyadh",
        "country": "Saudi Arabia",
        "method": 4,
    }
    save_config(custom_cfg)
    assert os.path.exists(config_file)

    loaded = load_config()
    assert loaded["language"] == "ar"
    assert loaded["city"] == "Riyadh"
    assert loaded["country"] == "Saudi Arabia"
    assert loaded["method"] == 4
    # Ensure merged defaults are present
    assert "prayers" in loaded
    assert "pause_duration_minutes" in loaded


def test_load_config_fallback_to_detect(isolated_tcalm_env, monkeypatch):
    # Ensure config file does not exist
    config_file = isolated_tcalm_env["config_file"]
    if os.path.exists(config_file):
        os.remove(config_file)

    mock_detected = consts.DEFAULT_CONFIG.copy()
    mock_detected["city"] = "Alexandria"

    import tcalm_core.config as cfg_mod
    monkeypatch.setattr(cfg_mod, "detect_location", lambda: mock_detected)

    loaded = load_config()
    assert loaded["city"] == "Alexandria"
    # Verify it was saved
    assert os.path.exists(config_file)
