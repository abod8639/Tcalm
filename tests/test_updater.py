import sys
import json
import pytest
from tcalm_core.updater import parse_version, check_for_updates, cmd_version
from tcalm_core.constants import VERSION
from tcalm_core.cli import main


def test_parse_version():
    assert parse_version("1.1.0") == (1, 1, 0)
    assert parse_version("v1.2.0") == (1, 2, 0)
    assert parse_version("v2.0.0-rc1") == (2, 0, 0)
    assert parse_version("v1.10.5") == (1, 10, 5)
    assert parse_version("") == (0, 0, 0)
    assert parse_version(None) == (0, 0, 0)


def test_check_for_updates_available(monkeypatch):
    class MockResponse:
        status = 200
        def read(self):
            return json.dumps({
                "tag_name": "v99.0.0",
                "html_url": "https://github.com/abod8639/Tcalm/releases/tag/v99.0.0"
            }).encode("utf-8")
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=3: MockResponse())
    result = check_for_updates()
    assert result["has_update"] is True
    assert result["latest_version"] == "99.0.0"
    assert result["current_version"] == VERSION
    assert result["error"] is None


def test_check_for_updates_up_to_date(monkeypatch):
    class MockResponse:
        status = 200
        def read(self):
            return json.dumps({
                "tag_name": f"v{VERSION}",
                "html_url": f"https://github.com/abod8639/Tcalm/releases/tag/v{VERSION}"
            }).encode("utf-8")
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=3: MockResponse())
    result = check_for_updates()
    assert result["has_update"] is False
    assert result["latest_version"] == VERSION
    assert result["error"] is None


def test_check_for_updates_network_error(monkeypatch):
    def mock_urlopen(req, timeout=3):
        raise ConnectionError("Network unreachable")

    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)
    result = check_for_updates()
    assert result["has_update"] is False
    assert result["error"] is not None


def test_cmd_version_output_with_update(monkeypatch, capsys):
    monkeypatch.setattr("tcalm_core.updater.check_for_updates", lambda: {
        "has_update": True,
        "current_version": "1.1.0",
        "latest_version": "1.2.0",
        "release_url": "https://github.com/abod8639/Tcalm/releases",
        "error": None
    })

    cmd_version({"language": "en"}, check_update=True)
    captured = capsys.readouterr().out
    assert "Tcalm version" in captured
    assert "A new version of Tcalm is available" in captured
    assert "v1.2.0" in captured


def test_cmd_version_output_up_to_date_arabic(monkeypatch, capsys):
    monkeypatch.setattr("tcalm_core.updater.check_for_updates", lambda: {
        "has_update": False,
        "current_version": "1.1.0",
        "latest_version": "1.1.0",
        "release_url": "https://github.com/abod8639/Tcalm/releases",
        "error": None
    })

    cmd_version({"language": "ar"}, check_update=True)
    captured = capsys.readouterr().out
    assert "Tcalm version" in captured
    assert "أنت تستخدم أحدث إصدار" in captured


def test_cli_update_command(monkeypatch, capsys):
    monkeypatch.setattr("tcalm_core.updater.check_for_updates", lambda: {
        "has_update": False,
        "current_version": VERSION,
        "latest_version": VERSION,
        "release_url": "https://github.com/abod8639/Tcalm/releases",
        "error": None
    })

    monkeypatch.setattr(sys, "argv", ["tcalm", "check-update"])
    main()
    captured = capsys.readouterr().out
    assert f"Tcalm version {VERSION}" in captured
