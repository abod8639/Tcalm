import platform
import subprocess
import pytest
from tcalm_core.media import (
    get_system_os,
    pause_media,
    send_notification,
    execute_adhan_pause,
)


def test_get_system_os(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    assert get_system_os() == "macos"

    monkeypatch.setattr(platform, "system", lambda: "Linux")
    assert get_system_os() == "linux"


def test_pause_media_linux_playerctl_success(monkeypatch):
    monkeypatch.setattr("tcalm_core.media.get_system_os", lambda: "linux")

    def mock_subprocess_run(cmd, **kwargs):
        if cmd[0] == "playerctl":
            return subprocess.CompletedProcess(cmd, returncode=0)
        return subprocess.CompletedProcess(cmd, returncode=1)

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    assert pause_media() is True


def test_pause_media_linux_dbus_fallback(monkeypatch):
    monkeypatch.setattr("tcalm_core.media.get_system_os", lambda: "linux")

    def mock_subprocess_run(cmd, **kwargs):
        if cmd[0] == "playerctl":
            raise FileNotFoundError("playerctl not found")
        if cmd[0] == "bash":
            return subprocess.CompletedProcess(cmd, returncode=0)
        return subprocess.CompletedProcess(cmd, returncode=1)

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    assert pause_media() is True


def test_pause_media_macos(monkeypatch):
    monkeypatch.setattr("tcalm_core.media.get_system_os", lambda: "macos")

    def mock_subprocess_run(cmd, **kwargs):
        if cmd[0] == "osascript":
            return subprocess.CompletedProcess(cmd, returncode=0)
        return subprocess.CompletedProcess(cmd, returncode=1)

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    assert pause_media() is True


def test_send_notification(monkeypatch):
    recorded_commands = []

    def mock_subprocess_run(cmd, **kwargs):
        recorded_commands.append(cmd)
        return subprocess.CompletedProcess(cmd, returncode=0)

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)

    # Test Linux notification
    monkeypatch.setattr("tcalm_core.media.get_system_os", lambda: "linux")
    send_notification("Asr", lang="ar")
    assert any("notify-send" in cmd for cmd in recorded_commands)

    # Test pre-adhan 1m notification
    recorded_commands.clear()
    send_notification("Asr", lang="ar", minutes_before=1)
    assert any("متبقي دقيقة" in str(cmd) for cmd in recorded_commands)

    # Test macOS notification
    recorded_commands.clear()
    monkeypatch.setattr("tcalm_core.media.get_system_os", lambda: "macos")
    send_notification("Maghrib", lang="en", minutes_before=1)
    assert any("1 minute until" in str(cmd) for cmd in recorded_commands)


def test_execute_adhan_pause(monkeypatch):
    paused = []
    notified = []

    monkeypatch.setattr("tcalm_core.media.pause_media", lambda: paused.append(True))
    monkeypatch.setattr("tcalm_core.media.send_notification", lambda p, lang, minutes_before=0: notified.append((p, minutes_before)))

    execute_adhan_pause("Dhuhr", duration_minutes=0, notify=True, lang="en", minutes_before=1)
    assert len(paused) == 1
    assert len(notified) == 1
    assert notified[0] == ("Dhuhr", 1)
