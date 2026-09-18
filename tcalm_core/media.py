import time
import platform
import subprocess
from tcalm_core.constants import PRAYER_NAMES_AR
from tcalm_core.config import log_message


def get_system_os():
    sys_name = platform.system().lower()
    if "darwin" in sys_name:
        return "macos"
    return "linux"


def pause_media():
    """Pauses media on Linux or macOS."""
    os_name = get_system_os()

    if os_name == "linux":
        # 1. Try playerctl
        try:
            res = subprocess.run(["playerctl", "-a", "pause"], capture_output=True, timeout=2)
            if res.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.SubprocessError):
            pass

        # 2. Try DBus MPRIS pause fallback
        try:
            dbus_cmd = (
                "for dest in $(dbus-send --session --dest=org.freedesktop.DBus --type=method_call "
                "--print-reply /org/freedesktop/DBus org.freedesktop.DBus.ListNames | grep -o 'org.mpris.MediaPlayer2[^\" ]*'); do "
                "dbus-send --session --dest=\"$dest\" --type=method_call /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Pause; "
                "done"
            )
            subprocess.run(["bash", "-c", dbus_cmd], capture_output=True, timeout=3)
            return True
        except Exception:
            pass

    elif os_name == "macos":
        applescript = """
        tell application "System Events"
            if (exists (processes where name is "Spotify")) then
                tell application "Spotify" to pause
            end if
            if (exists (processes where name is "Music")) then
                tell application "Music" to pause
            end if
            if (exists (processes where name is "QuickTime Player")) then
                tell application "QuickTime Player" to pause every document
            end if
            if (exists (processes where name is "Google Chrome")) then
                tell application "Google Chrome"
                    repeat with w in windows
                        repeat with t in tabs of w
                            try
                                execute t javascript "document.querySelectorAll('video, audio').forEach(el => el.pause());"
                            end try
                        end repeat
                    end repeat
                end tell
            end if
            if (exists (processes where name is "Brave Browser")) then
                tell application "Brave Browser"
                    repeat with w in windows
                        repeat with t in tabs of w
                            try
                                execute t javascript "document.querySelectorAll('video, audio').forEach(el => el.pause());"
                            end try
                        end repeat
                    end repeat
                end tell
            end if
            if (exists (processes where name is "Safari")) then
                tell application "Safari"
                    repeat with w in windows
                        repeat with t in tabs of w
                            try
                                do JavaScript "document.querySelectorAll('video, audio').forEach(el => el.pause());" in t
                            end try
                        end repeat
                    end repeat
                end tell
            end if
        end tell
        """
        try:
            subprocess.run(["osascript", "-e", applescript], capture_output=True, timeout=5)
            return True
        except Exception:
            pass

    return False


def send_notification(prayer_name):
    """Sends a desktop notification on Linux or macOS."""
    arabic_name = PRAYER_NAMES_AR.get(prayer_name, prayer_name)
    title = f"حان الآن موعد أذان {arabic_name}"
    body = "تم إيقاف الوسائط مؤقتاً (Tcalm)"

    os_name = get_system_os()
    if os_name == "linux":
        try:
            subprocess.run(
                ["notify-send", "-a", "Tcalm", "-u", "normal", title, body],
                capture_output=True,
                timeout=3
            )
        except Exception:
            pass
    elif os_name == "macos":
        try:
            script = f'display notification "{body}" with title "{title}" subtitle "Tcalm"'
            subprocess.run(["osascript", "-e", script], capture_output=True, timeout=3)
        except Exception:
            pass


def execute_adhan_pause(prayer_name, duration_minutes=0, notify=True):
    """Executes media pause and optional duration hold."""
    arabic_name = PRAYER_NAMES_AR.get(prayer_name, prayer_name)
    log_message(f"Triggering Adhan pause for {prayer_name} ({arabic_name}).")

    pause_media()
    if notify:
        send_notification(prayer_name)

    if duration_minutes > 0:
        end_time = time.time() + (duration_minutes * 60)
        while time.time() < end_time:
            time.sleep(5)
            pause_media()
