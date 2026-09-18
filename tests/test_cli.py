import sys
import json
from datetime import date
import pytest
from tcalm_core.cli import main, cmd_status, cmd_list, cmd_test, cmd_config
from tcalm_core.constants import VERSION, DEFAULT_CONFIG


def test_cli_version(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["tcalm", "version"])
    main()
    captured = capsys.readouterr()
    assert f"Tcalm version {VERSION}" in captured.out


def test_cli_status(monkeypatch, capsys, isolated_tcalm_env):
    mock_timings = {
        "Fajr": "04:30",
        "Dhuhr": "12:00",
        "Asr": "15:30",
        "Maghrib": "18:00",
        "Isha": "19:30",
    }
    monkeypatch.setattr("tcalm_core.cli.get_prayer_times", lambda cfg, dt: mock_timings)
    monkeypatch.setattr("tcalm_core.config.detect_location", lambda: DEFAULT_CONFIG.copy())

    monkeypatch.setattr(sys, "argv", ["tcalm", "status"])
    main()
    captured = capsys.readouterr()
    assert "Status" in captured.out or "الحالة" in captured.out
    assert "Cairo" in captured.out or "Egypt" in captured.out


def test_cli_list(monkeypatch, capsys, isolated_tcalm_env):
    mock_timings = {
        "Fajr": "04:30",
        "Dhuhr": "12:00",
        "Asr": "15:30",
        "Maghrib": "18:00",
        "Isha": "19:30",
    }
    monkeypatch.setattr("tcalm_core.cli.get_prayer_times", lambda cfg, dt: mock_timings)

    monkeypatch.setattr(sys, "argv", ["tcalm", "list"])
    main()
    captured = capsys.readouterr()
    assert "Fajr" in captured.out or "الفجر" in captured.out
    assert "04:30" in captured.out


def test_cli_test_command(monkeypatch, capsys):
    paused_called = []
    notified_called = []
    monkeypatch.setattr("tcalm_core.cli.pause_media", lambda: paused_called.append(True) or True)
    monkeypatch.setattr("tcalm_core.cli.send_notification", lambda p, lang: notified_called.append(p))

    monkeypatch.setattr(sys, "argv", ["tcalm", "test"])
    main()
    captured = capsys.readouterr()
    assert len(paused_called) == 1
    assert len(notified_called) == 1


def test_cli_config_json(monkeypatch, capsys, isolated_tcalm_env):
    monkeypatch.setattr(sys, "argv", ["tcalm", "config", "--json"])
    main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "city" in data
    assert "country" in data


def test_cli_config_modify(monkeypatch, capsys, isolated_tcalm_env):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tcalm",
            "config",
            "--city",
            "Makkah",
            "--country",
            "Saudi Arabia",
            "--method",
            "4",
            "--duration",
            "5",
            "--language",
            "ar",
        ],
    )
    main()
    captured = capsys.readouterr()
    assert "الإعدادات" in captured.out or "saved" in captured.out.lower()

    # Verify updated config via --json
    monkeypatch.setattr(sys, "argv", ["tcalm", "config", "--json"])
    main()
    captured_json = capsys.readouterr()
    cfg = json.loads(captured_json.out)
    assert cfg["city"] == "Makkah"
    assert cfg["country"] == "Saudi Arabia"
    assert cfg["method"] == 4
    assert cfg["pause_duration_minutes"] == 5
    assert cfg["language"] == "ar"


def test_cli_stop_not_running(monkeypatch, capsys, isolated_tcalm_env):
    monkeypatch.setattr("tcalm_core.cli.get_daemon_pid", lambda: None)
    monkeypatch.setattr(sys, "argv", ["tcalm", "stop"])
    main()
    captured = capsys.readouterr()
    assert "not running" in captured.out.lower() or "غير مشغلة" in captured.out
