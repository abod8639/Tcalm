import os
import sys
import time
import signal
from datetime import datetime, timedelta
from tcalm_core.constants import PID_FILE
from tcalm_core.config import ensure_config_dir, log_message, load_config
from tcalm_core.prayer import get_prayer_times
from tcalm_core.media import execute_adhan_pause


def is_pid_running(pid):
    """Check if process with given PID is alive."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def get_daemon_pid():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
                if is_pid_running(pid):
                    return pid
        except Exception:
            pass
    return None


def daemon_loop():
    """Main background loop with smart sleeping and DST responsiveness."""
    ensure_config_dir()

    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    log_message(f"Tcalm daemon started with PID {os.getpid()}")

    def cleanup_and_exit(signum, frame):
        log_message(f"Tcalm daemon received signal {signum}. Exiting cleanly.")
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGTERM, cleanup_and_exit)
    signal.signal(signal.SIGINT, cleanup_and_exit)

    last_handled = {}

    while True:
        try:
            cfg = load_config()
            now = datetime.now()
            today_date = now.date()
            timings = get_prayer_times(cfg, today_date)

            allowed_prayers = cfg.get("prayers", ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"])
            duration = cfg.get("pause_duration_minutes", 0)
            notify = cfg.get("notifications", True)

            upcoming_prayers = []
            for p_name in allowed_prayers:
                t_str = timings.get(p_name)
                if not t_str:
                    continue
                hh, mm = map(int, t_str.split(":"))
                p_dt = datetime(now.year, now.month, now.day, hh, mm, 0)

                key = f"{today_date}_{p_name}"
                diff_secs = (now - p_dt).total_seconds()

                if 0 <= diff_secs < 60 and key not in last_handled:
                    last_handled[key] = True
                    execute_adhan_pause(p_name, duration, notify)
                elif p_dt > now:
                    upcoming_prayers.append((p_dt, p_name))

            if upcoming_prayers:
                next_dt, next_name = min(upcoming_prayers, key=lambda x: x[0])
                wait_seconds = (next_dt - now).total_seconds()
            else:
                tomorrow = today_date + timedelta(days=1)
                midnight = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 5)
                wait_seconds = (midnight - now).total_seconds()

            sleep_chunk = 15
            sleep_cycles = max(1, int(min(wait_seconds, 60) / sleep_chunk))
            for _ in range(sleep_cycles):
                time.sleep(sleep_chunk)

        except Exception as e:
            log_message(f"Unexpected error in daemon loop: {e}")
            time.sleep(30)
