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
