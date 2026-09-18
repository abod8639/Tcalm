import os
import sys
import time
import json
import signal
import shutil
import argparse
import subprocess
from datetime import datetime

from tcalm_core.constants import (
    VERSION,
    PID_FILE,
    LOG_FILE,
    CACHE_FILE,
    PRAYER_NAMES_AR,
    CALCULATION_METHODS,
)
from tcalm_core.config import (
    ensure_config_dir,
    load_config,
    save_config,
)
from tcalm_core.geo import detect_location
from tcalm_core.prayer import get_prayer_times
from tcalm_core.media import pause_media, send_notification
from tcalm_core.daemon import is_pid_running, get_daemon_pid, daemon_loop


def cmd_start():
    pid = get_daemon_pid()
    if pid:
        print(f"[*] Tcalm is already running (PID: {pid}).")
        return

    ensure_config_dir()

    tcalm_bin = shutil.which("tcalm")
    if os.path.isabs(sys.argv[0]) or os.path.exists(sys.argv[0]):
        candidate = os.path.abspath(sys.argv[0])
        if os.path.basename(candidate) == "tcalm" and os.path.isfile(candidate):
            tcalm_bin = candidate

    if tcalm_bin and os.path.isfile(tcalm_bin):
        cmd = [sys.executable, tcalm_bin, "run"]
    else:
        cmd = [sys.executable, "-m", "tcalm_core", "run"]

    with open(LOG_FILE, "a") as log_f:
        proc = subprocess.Popen(
            cmd,
            stdout=log_f,
            stderr=log_f,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

    time.sleep(0.5)
    if is_pid_running(proc.pid):
        print(f"[✓] Tcalm daemon started successfully (PID: {proc.pid}).")
        cfg = load_config()
        print_status_summary(cfg)
    else:
        print(f"[!] Failed to start Tcalm daemon. Check {LOG_FILE} for details.")


def cmd_stop():
    pid = get_daemon_pid()
    if not pid:
        print("[-] Tcalm is not running.")
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except Exception:
                pass
        return

    print(f"[*] Stopping Tcalm daemon (PID: {pid})...")
    try:
        os.kill(pid, signal.SIGTERM)
        for _ in range(30):
            time.sleep(0.1)
            if not is_pid_running(pid):
                break
        else:
            os.kill(pid, signal.SIGKILL)
    except Exception as e:
        print(f"[!] Error stopping process: {e}")

    if os.path.exists(PID_FILE):
        try:
            os.remove(PID_FILE)
        except Exception:
            pass

    print("[✓] Tcalm daemon stopped.")


def cmd_restart():
    cmd_stop()
    time.sleep(0.5)
    cmd_start()


def print_status_summary(cfg):
    now = datetime.now()
    timings = get_prayer_times(cfg, now.date())

    upcoming = []
    for p in cfg.get("prayers", ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]):
        t_str = timings.get(p)
        if t_str:
            hh, mm = map(int, t_str.split(":"))
            p_dt = datetime(now.year, now.month, now.day, hh, mm, 0)
            if p_dt > now:
                upcoming.append((p_dt, p))

    if upcoming:
        next_dt, next_name = min(upcoming, key=lambda x: x[0])
        diff = next_dt - now
        hours, remainder = divmod(int(diff.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        ar_name = PRAYER_NAMES_AR.get(next_name, next_name)
        time_left_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        print(f"    Next Prayer: {next_name} ({ar_name}) at {timings[next_name]} (in {time_left_str})")
    else:
        print("    Next Prayer: Fajr tomorrow morning.")


def cmd_status():
    pid = get_daemon_pid()
    cfg = load_config()

    print("==================================================")
    print("                 Tcalm Status                     ")
    print("==================================================")

    if pid:
        print(f"  ● Status:           RUNNING (PID: {pid})")
    else:
        print("  ○ Status:           STOPPED")

    utc_offset = datetime.now().astimezone().strftime("%z")
    formatted_offset = f"UTC{utc_offset[:3]}:{utc_offset[3:]}"
    dst_status = "Active (صيفي)" if time.localtime().tm_isdst > 0 else "Inactive (شتوي)"

    print(f"  ● Location:         {cfg.get('city')}, {cfg.get('country')}")
    print(f"  ● Timezone:         {cfg.get('timezone')} ({formatted_offset}, DST: {dst_status})")
    print(f"  ● Coordinates:      Lat: {cfg.get('latitude')}, Lng: {cfg.get('longitude')}")
    print(f"  ● Method:           {CALCULATION_METHODS.get(cfg.get('method', 5), 'Custom')}")
    dur = cfg.get("pause_duration_minutes", 0)
    print(f"  ● Pause Action:     {'Single Pause (مرة واحدة)' if dur == 0 else f'Hold for {dur} minutes'}")
    print("--------------------------------------------------")

    print_status_summary(cfg)
    print("==================================================")


def cmd_list():
    cfg = load_config()
    now = datetime.now()
    timings = get_prayer_times(cfg, now.date())

    print(f"\nPrayer Times for {cfg.get('city')}, {cfg.get('country')} ({now.strftime('%Y-%m-%d')}):")
    print("--------------------------------------------------")
    print(" Prayer      | الصلاة       | Time      | Status   ")
    print("--------------------------------------------------")

    allowed = cfg.get("prayers", ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"])
    for p in allowed:
        t_str = timings.get(p, "--:--")
        ar_name = PRAYER_NAMES_AR.get(p, p)

        status = ""
        if t_str != "--:--":
            hh, mm = map(int, t_str.split(":"))
            p_dt = datetime(now.year, now.month, now.day, hh, mm, 0)
            if p_dt < now:
                status = "Passed"
            else:
                diff = p_dt - now
                hours, rem = divmod(int(diff.total_seconds()), 3600)
                minutes, _ = divmod(rem, 60)
                status = f"in {hours}h {minutes}m" if hours > 0 else f"in {minutes}m"

        print(f" {p:<11} | {ar_name:<12} | {t_str:<9} | {status}")
    print("--------------------------------------------------\n")


def cmd_test():
    print("[*] Testing media pause and desktop notification...")
    paused = pause_media()
    send_notification("Dhuhr")
    print(f"[✓] Media pause triggered (Success: {paused}).")
    print("[✓] Notification sent. You should see a desktop banner.")


def cmd_config(args):
    has_flags = any([
        args.auto_detect,
        args.city is not None,
        args.country is not None,
        args.timezone is not None,
        args.lat is not None,
        args.lng is not None,
        args.method is not None,
        args.duration is not None,
        args.notifications is not None,
        getattr(args, "json", False),
    ])

    if not has_flags:
        from tcalm_core.tui import run_config_tui
        run_config_tui()
        return

    if getattr(args, "json", False):
        cfg = load_config()
        print(json.dumps(cfg, indent=2, ensure_ascii=False))
        return

    cfg = load_config()
    modified = False

    if args.auto_detect:
        print("[*] Detecting location and timezone automatically...")
        cfg = detect_location()
        modified = True
        print(f"[✓] Detected: {cfg.get('city')}, {cfg.get('country')} ({cfg.get('timezone')})")

    if args.city:
        cfg["city"] = args.city
        modified = True
    if args.country:
        cfg["country"] = args.country
        modified = True
    if args.timezone:
        cfg["timezone"] = args.timezone
        modified = True
    if args.lat is not None and args.lng is not None:
        cfg["latitude"] = args.lat
        cfg["longitude"] = args.lng
        modified = True
    if args.method is not None:
        if args.method in CALCULATION_METHODS:
            cfg["method"] = args.method
            modified = True
        else:
            print("[!] Invalid method. Choose from 1 to 15.")
    if args.duration is not None:
        cfg["pause_duration_minutes"] = max(0, args.duration)
        modified = True
    if args.notifications is not None:
        cfg["notifications"] = (args.notifications.lower() in ["true", "1", "yes"])
        modified = True

    if modified:
        save_config(cfg)
        if os.path.exists(CACHE_FILE):
            try:
                os.remove(CACHE_FILE)
            except Exception:
                pass
        print("[✓] Configuration updated successfully.")

        if get_daemon_pid():
            print("[*] Restarting running daemon to apply changes...")
            cmd_restart()


def main():
    parser = argparse.ArgumentParser(
        description="Tcalm - Prayer Time Media Pauser for Linux & macOS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tcalm start                   Start background daemon
  tcalm stop                    Stop background daemon
  tcalm status                  Check service status and next prayer
  tcalm list                    List today's prayer times
  tcalm test                    Test media pause & notification
  tcalm config --city "Cairo"   Set city manually
  tcalm config --duration 10    Keep media paused for 10 minutes
  tcalm config --auto-detect    Re-detect location via IP
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("start", help="Start background daemon")
    subparsers.add_parser("stop", help="Stop background daemon")
    subparsers.add_parser("restart", help="Restart background daemon")
    subparsers.add_parser("status", help="Show current status and next prayer")
    subparsers.add_parser("list", help="List today's prayer times")
    subparsers.add_parser("test", help="Test media pause and notification")
    subparsers.add_parser("run", help="Run in foreground (for systemd or debugging)")

    cfg_parser = subparsers.add_parser("config", help="View or modify configuration")
    cfg_parser.add_argument("--city", type=str, help="Set city name")
    cfg_parser.add_argument("--country", type=str, help="Set country name")
    cfg_parser.add_argument("--timezone", type=str, help="Set timezone (e.g. Africa/Cairo)")
    cfg_parser.add_argument("--lat", type=float, help="Set latitude")
    cfg_parser.add_argument("--lng", type=float, help="Set longitude")
    cfg_parser.add_argument("--method", type=int, help="Calculation method (1-15)")
    cfg_parser.add_argument("--duration", type=int, help="Pause duration in minutes (0 for single pause)")
    cfg_parser.add_argument("--notifications", type=str, help="Enable or disable desktop notifications (true/false)")
    cfg_parser.add_argument("--auto-detect", action="store_true", help="Auto-detect location and timezone")
    cfg_parser.add_argument("--json", action="store_true", help="Print configuration in JSON format without interactive TUI")

    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.command == "start":
        cmd_start()
    elif args.command == "stop":
        cmd_stop()
    elif args.command == "restart":
        cmd_restart()
    elif args.command == "status":
        cmd_status()
    elif args.command == "list":
        cmd_list()
    elif args.command == "test":
        cmd_test()
    elif args.command == "run":
        daemon_loop()
    elif args.command == "config":
        cmd_config(args)
    elif args.command == "version":
        print(f"Tcalm version {VERSION}")
    else:
        cmd_status()
