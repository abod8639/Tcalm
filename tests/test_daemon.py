import os
import pytest
from tcalm_core.daemon import (
    is_pid_running,
    get_daemon_pid,
)


def test_is_pid_running():
    current_pid = os.getpid()
    assert is_pid_running(current_pid) is True

    # High unlikely PID
    assert is_pid_running(9999999) is False


def test_get_daemon_pid(isolated_tcalm_env):
    pid_file = isolated_tcalm_env["pid_file"]

    # When file doesn't exist
    assert get_daemon_pid() is None

    # When file exists with current live PID
    current_pid = os.getpid()
    with open(pid_file, "w") as f:
        f.write(str(current_pid))
    assert get_daemon_pid() == current_pid

    # When file exists with dead PID
    with open(pid_file, "w") as f:
        f.write("9999999")
    assert get_daemon_pid() is None


def test_daemon_loop_triggers_pre_adhan(monkeypatch, isolated_tcalm_env):
    from datetime import datetime as real_datetime
    from tcalm_core.constants import DEFAULT_CONFIG
    from tcalm_core.daemon import daemon_loop

    cfg = DEFAULT_CONFIG.copy()
    cfg["pause_before_minutes"] = 1
    cfg["prayers"] = ["Dhuhr"]

    fake_now = real_datetime(2026, 9, 22, 11, 59, 10)

    class FakeDateTime(real_datetime):
        @classmethod
        def now(cls, tz=None):
            return fake_now

    monkeypatch.setattr("tcalm_core.daemon.datetime", FakeDateTime)
    monkeypatch.setattr("tcalm_core.daemon.load_config", lambda: cfg)
    monkeypatch.setattr("tcalm_core.daemon.get_prayer_times", lambda c, d: {"Dhuhr": "12:00"})

    executed = []

    def mock_execute(p_name, duration, notify, lang="en", minutes_before=0):
        executed.append((p_name, duration, notify, minutes_before))
        raise KeyboardInterrupt("Stop loop")

    monkeypatch.setattr("tcalm_core.daemon.execute_adhan_pause", mock_execute)

    with pytest.raises(KeyboardInterrupt):
        daemon_loop()

    assert len(executed) == 1
    assert executed[0] == ("Dhuhr", 0, True, 1)
