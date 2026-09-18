import os
import sys
import pytest
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def isolated_tcalm_env(tmp_path, monkeypatch):
    """Isolate all configuration, cache, PID, and log files in a temporary directory."""
    test_config_dir = tmp_path / ".config" / "tcalm"
    test_config_dir.mkdir(parents=True, exist_ok=True)

    test_config_file = str(test_config_dir / "config.json")
    test_pid_file = str(test_config_dir / "tcalm.pid")
    test_log_file = str(test_config_dir / "tcalm.log")
    test_cache_file = str(test_config_dir / "cache.json")
    test_dir_str = str(test_config_dir)

    # Patch constants module
    import tcalm_core.constants as consts
    monkeypatch.setattr(consts, "CONFIG_DIR", test_dir_str)
    monkeypatch.setattr(consts, "CONFIG_FILE", test_config_file)
    monkeypatch.setattr(consts, "PID_FILE", test_pid_file)
    monkeypatch.setattr(consts, "LOG_FILE", test_log_file)
    monkeypatch.setattr(consts, "CACHE_FILE", test_cache_file)

    # Patch config module
    import tcalm_core.config as cfg_mod
    monkeypatch.setattr(cfg_mod, "CONFIG_DIR", test_dir_str)
    monkeypatch.setattr(cfg_mod, "CONFIG_FILE", test_config_file)
    monkeypatch.setattr(cfg_mod, "LOG_FILE", test_log_file)

    # Patch prayer module
    import tcalm_core.prayer as prayer_mod
    monkeypatch.setattr(prayer_mod, "CACHE_FILE", test_cache_file)

    # Patch daemon module
    import tcalm_core.daemon as daemon_mod
    monkeypatch.setattr(daemon_mod, "PID_FILE", test_pid_file)

    # Patch cli module
    import tcalm_core.cli as cli_mod
    monkeypatch.setattr(cli_mod, "PID_FILE", test_pid_file)
    monkeypatch.setattr(cli_mod, "LOG_FILE", test_log_file)
    monkeypatch.setattr(cli_mod, "CACHE_FILE", test_cache_file)

    return {
        "config_dir": test_dir_str,
        "config_file": test_config_file,
        "pid_file": test_pid_file,
        "log_file": test_log_file,
        "cache_file": test_cache_file,
    }
