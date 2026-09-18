import os
import sys
import json
import tty
import termios
from datetime import datetime

from tcalm_core.constants import (
    CALCULATION_METHODS,
    CACHE_FILE,
)
from tcalm_core.config import (
    load_config,
    save_config,
)
from tcalm_core.geo import detect_location
from tcalm_core.daemon import get_daemon_pid

# Colors and styling
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RED = "\033[31m"
CLEAR_SCREEN = "\033[2J\033[H"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

COUNTRIES_DATA = [
    {
        "name": "Egypt (مصر)",
        "country": "Egypt",
        "method": 5,
        "timezone": "Africa/Cairo",
        "lat": 30.0444, "lng": 31.2357,
        "cities": [
            ("Cairo (القاهرة)", 30.0444, 31.2357),
            ("Alexandria (الإسكندرية)", 31.2001, 29.9187),
            ("Giza (الجيزة)", 30.0131, 31.2089),
            ("Mansoura (المنصورة)", 31.0409, 31.3785),
            ("Tanta (طنطا)", 30.7865, 31.0004),
            ("Assiut (أسيوط)", 27.1783, 31.1859),
            ("Sohag (سوهاج)", 26.5569, 31.6948),
            ("Luxor (الأقصر)", 25.6872, 32.6396),
            ("Aswan (أسوان)", 24.0889, 32.8998),
            ("Port Said (بورسعيد)", 31.2653, 32.3019),
            ("Suez (السويس)", 29.9668, 32.5498),
            ("Hurghada (الغردقة)", 27.2579, 33.8116),
            ("Sharm El-Sheikh (شرم الشيخ)", 27.9158, 34.3299),
        ]
    },
    {
        "name": "Saudi Arabia (المملكة العربية السعودية)",
        "country": "Saudi Arabia",
        "method": 4,
        "timezone": "Asia/Riyadh",
        "lat": 24.7136, "lng": 46.6753,
        "cities": [
            ("Makkah (مكة المكرمة)", 21.3891, 39.8579),
            ("Madinah (المدينة المنورة)", 24.5247, 39.5692),
            ("Riyadh (الرياض)", 24.7136, 46.6753),
            ("Jeddah (جدة)", 21.5433, 39.1728),
            ("Dammam (الدمام)", 26.4207, 50.0888),
            ("Khobar (الخبر)", 26.2172, 50.1971),
            ("Taif (الطائف)", 21.2854, 40.4222),
            ("Tabuk (تبوك)", 28.3835, 36.5662),
            ("Abha (أبها)", 18.2164, 42.5053),
            ("Buraidah (بريدة)", 26.3260, 43.9750),
        ]
    },
    {
        "name": "United Arab Emirates (الإمارات العربية المتحدة)",
        "country": "United Arab Emirates",
        "method": 8,
        "timezone": "Asia/Dubai",
        "lat": 25.2048, "lng": 55.2708,
        "cities": [
            ("Abu Dhabi (أبوظبي)", 24.4539, 54.3773),
            ("Dubai (دبي)", 25.2048, 55.2708),
            ("Sharjah (الشارقة)", 25.3463, 55.4209),
            ("Ajman (عجمان)", 25.4052, 55.5136),
            ("Ras Al Khaimah (رأس الخيمة)", 25.7895, 55.9432),
            ("Al Ain (العين)", 24.2075, 55.7447),
        ]
    },
    {
        "name": "Kuwait (الكويت)",
        "country": "Kuwait",
        "method": 9,
        "timezone": "Asia/Kuwait",
        "lat": 29.3759, "lng": 47.9774,
        "cities": [
            ("Kuwait City (مدينة الكويت)", 29.3759, 47.9774),
            ("Hawalli (حولي)", 29.3328, 48.0282),
            ("Salmiya (السالمية)", 29.3344, 48.0772),
            ("Ahmadi (الأحمدي)", 29.0769, 48.0839),
        ]
    },
    {
        "name": "Qatar (قطر)",
        "country": "Qatar",
        "method": 10,
        "timezone": "Asia/Qatar",
        "lat": 25.2854, "lng": 51.5310,
        "cities": [
            ("Doha (الدوحة)", 25.2854, 51.5310),
            ("Al Rayyan (الريان)", 25.2919, 51.4244),
            ("Al Wakrah (الوكرة)", 25.1768, 51.6048),
        ]
    },
    {
        "name": "Bahrain (البحرين)",
        "country": "Bahrain",
        "method": 8,
        "timezone": "Asia/Bahrain",
        "lat": 26.2285, "lng": 50.5860,
        "cities": [
            ("Manama (المنامة)", 26.2285, 50.5860),
            ("Riffa (الرفاع)", 26.1300, 50.5550),
            ("Muharraq (المحرق)", 26.2572, 50.6119),
        ]
    },
    {
        "name": "Oman (سلطنة عمان)",
        "country": "Oman",
        "method": 8,
        "timezone": "Asia/Muscat",
        "lat": 23.5880, "lng": 58.3829,
        "cities": [
            ("Muscat (مسقط)", 23.5880, 58.3829),
            ("Salalah (صلالة)", 17.0151, 54.0924),
            ("Sohar (صحار)", 24.3461, 56.7075),
            ("Nizwa (نزوى)", 22.9333, 57.5333),
        ]
    },
    {
        "name": "Jordan (الأردن)",
        "country": "Jordan",
        "method": 3,
        "timezone": "Asia/Amman",
        "lat": 31.9454, "lng": 35.9284,
        "cities": [
            ("Amman (عمّان)", 31.9454, 35.9284),
            ("Zarqa (الزرقاء)", 32.0728, 36.0880),
            ("Irbid (إربد)", 32.5568, 35.8469),
            ("Aqaba (العقبة)", 29.5321, 35.0063),
        ]
    },
    {
        "name": "Palestine (فلسطين)",
        "country": "Palestine",
        "method": 3,
        "timezone": "Asia/Gaza",
        "lat": 31.9522, "lng": 35.2332,
        "cities": [
            ("Jerusalem / Al-Quds (القدس الشريف)", 31.7683, 35.2137),
            ("Gaza (غزة)", 31.5017, 34.4668),
            ("Ramallah (رام الله)", 31.9038, 35.2034),
            ("Nablus (نابلس)", 32.2211, 35.2544),
            ("Hebron (الخليل)", 31.5326, 35.0998),
        ]
    },
    {
        "name": "Iraq (العراق)",
        "country": "Iraq",
        "method": 3,
        "timezone": "Asia/Baghdad",
        "lat": 33.3152, "lng": 44.3661,
        "cities": [
            ("Baghdad (بغداد)", 33.3152, 44.3661),
            ("Basra (البصرة)", 30.5081, 47.7835),
            ("Erbil (أربيل)", 36.1911, 44.0092),
            ("Mosul (الموصل)", 36.3400, 43.1300),
            ("Najaf (النجف)", 32.0259, 44.3462),
        ]
    },
    {
        "name": "Morocco (المغرب)",
        "country": "Morocco",
        "method": 3,
        "timezone": "Africa/Casablanca",
        "lat": 33.5731, "lng": -7.5898,
        "cities": [
            ("Casablanca (الدار البيضاء)", 33.5731, -7.5898),
            ("Rabat (الرباط)", 34.0209, -6.8416),
            ("Marrakech (مراكش)", 31.6295, -7.9811),
            ("Fes (فاس)", 34.0331, -5.0003),
            ("Tangier (طنجة)", 35.7595, -5.8340),
        ]
    },
    {
        "name": "Algeria (الجزائر)",
        "country": "Algeria",
        "method": 3,
        "timezone": "Africa/Algiers",
        "lat": 36.7538, "lng": 3.0588,
        "cities": [
            ("Algiers (الجزائر العاصمة)", 36.7538, 3.0588),
            ("Oran (وهران)", 35.6987, -0.6349),
            ("Constantine (قسنطينة)", 36.3650, 6.6147),
        ]
    },
    {
        "name": "Tunisia (تونس)",
        "country": "Tunisia",
        "method": 3,
        "timezone": "Africa/Tunis",
        "lat": 36.8065, "lng": 10.1815,
        "cities": [
            ("Tunis (تونس العاصمة)", 36.8065, 10.1815),
            ("Sfax (صفاقس)", 34.7406, 10.7603),
            ("Sousse (سوسة)", 35.8256, 10.6369),
        ]
    },
    {
        "name": "Turkey (تركيا)",
        "country": "Turkey",
        "method": 13,
        "timezone": "Europe/Istanbul",
        "lat": 41.0082, "lng": 28.9784,
        "cities": [
            ("Istanbul (إسطنبول)", 41.0082, 28.9784),
            ("Ankara (أنقرة)", 39.9334, 32.8597),
            ("Izmir (إزمير)", 38.4237, 27.1428),
            ("Bursa (بورصة)", 40.1828, 29.0667),
            ("Antalya (أنطاليا)", 36.8969, 30.7133),
        ]
    },
    {
        "name": "United Kingdom",
        "country": "United Kingdom",
        "method": 3,
        "timezone": "Europe/London",
        "lat": 51.5074, "lng": -0.1278,
        "cities": [
            ("London", 51.5074, -0.1278),
            ("Birmingham", 52.4862, -1.8904),
            ("Manchester", 53.4808, -2.2426),
        ]
    },
    {
        "name": "United States",
        "country": "United States",
        "method": 2,
        "timezone": "America/New_York",
        "lat": 40.7128, "lng": -74.0060,
        "cities": [
            ("New York", 40.7128, -74.0060),
            ("Chicago", 41.8781, -87.6298),
            ("Los Angeles", 34.0522, -118.2437),
            ("Houston", 29.7604, -95.3698),
        ]
    },
]

COMMON_TIMEZONES = [
    "Africa/Cairo",
    "Asia/Riyadh",
    "Asia/Dubai",
    "Asia/Kuwait",
    "Asia/Qatar",
    "Asia/Bahrain",
    "Asia/Muscat",
    "Asia/Amman",
    "Asia/Gaza",
    "Asia/Jerusalem",
    "Asia/Baghdad",
    "Asia/Beirut",
    "Asia/Damascus",
    "Africa/Casablanca",
    "Africa/Algiers",
    "Africa/Tunis",
    "Africa/Tripoli",
    "Africa/Khartoum",
    "Europe/Istanbul",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "America/New_York",
    "America/Chicago",
    "America/Los_Angeles",
    "Asia/Karachi",
    "Asia/Dhaka",
    "Asia/Kolkata",
    "Asia/Jakarta",
    "Asia/Kuala_Lumpur",
]


def read_key():
    """Reads a single keypress or ANSI escape sequence."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                ch3 = sys.stdin.read(1)
                if ch3 == 'A':
                    return 'UP'
                elif ch3 == 'B':
                    return 'DOWN'
                elif ch3 == 'C':
                    return 'RIGHT'
                elif ch3 == 'D':
                    return 'LEFT'
            return 'ESC'
        elif ch in ('\r', '\n'):
            return 'ENTER'
        elif ch == '\x03':  # Ctrl+C
            raise KeyboardInterrupt
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def select_menu(title, options, initial_index=0):
    """
    Renders an interactive selection list navigable with UP/DOWN arrows.
    options is a list of strings or (display_label, value) tuples.
    Returns the selected value (or index), or None if canceled.
    """
    selected = initial_index
    page_size = 12
    offset = 0

    num_items = len(options)
    if num_items == 0:
        return None

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    try:
        while True:
            # Adjust offset for pagination scrolling
            if selected < offset:
                offset = selected
            elif selected >= offset + page_size:
                offset = selected - page_size + 1

            # Render
            lines = [CLEAR_SCREEN]
            lines.append(f"{BOLD}{BLUE}=================================================={RESET}")
            lines.append(f"  {BOLD}{title}{RESET}")
            lines.append(f"{BOLD}{BLUE}=================================================={RESET}")
            lines.append(f"{DIM}Use [↑/↓] arrows to navigate, [Enter] to select, [Esc] to return{RESET}\n")

            visible_items = options[offset:offset + page_size]
            for i, opt in enumerate(visible_items):
                actual_idx = offset + i
                label = opt[0] if isinstance(opt, tuple) else str(opt)
                if actual_idx == selected:
                    lines.append(f"  {BOLD}{CYAN}❯ {label}{RESET}")
                else:
                    lines.append(f"    {label}")

            if num_items > page_size:
                lines.append(f"\n{DIM}  ({selected + 1}/{num_items}){RESET}")

            lines.append(f"\n{BOLD}{BLUE}--------------------------------------------------{RESET}")
            sys.stdout.write("\n".join(lines) + "\n")
            sys.stdout.flush()

            key = read_key()
            if key == 'UP':
                selected = (selected - 1) % num_items
            elif key == 'DOWN':
                selected = (selected + 1) % num_items
            elif key == 'ENTER':
                chosen = options[selected]
                return chosen[1] if isinstance(chosen, tuple) else chosen
            elif key in ('ESC', 'q', 'Q'):
                return None
    finally:
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()


def choose_country_and_city(cfg):
    """Wizard to select country and corresponding city."""
    country_options = [(c["name"], c) for c in COUNTRIES_DATA]
    country_options.append(("Custom / Manual Entry...", "CUSTOM"))

    chosen_country = select_menu("Select Country", country_options)
    if not chosen_country:
        return False

    if chosen_country == "CUSTOM":
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.write(f"{BOLD}Enter Country Name:{RESET} ")
        sys.stdout.flush()
        c_name = input().strip()
        if not c_name:
            return False
        sys.stdout.write(f"{BOLD}Enter City Name:{RESET} ")
        sys.stdout.flush()
        city_name = input().strip()
        if not city_name:
            return False

        cfg["country"] = c_name
        cfg["city"] = city_name
        cfg["auto_detect"] = False
        return True

    cfg["country"] = chosen_country["country"]
    cfg["method"] = chosen_country["method"]
    cfg["timezone"] = chosen_country["timezone"]
    cfg["latitude"] = chosen_country["lat"]
    cfg["longitude"] = chosen_country["lng"]
    cfg["auto_detect"] = False

    # Choose city
    city_options = [(c[0], c) for c in chosen_country["cities"]]
    city_options.append(("Enter City Manually...", "MANUAL"))

    chosen_city = select_menu(f"Select City in {chosen_country['country']}", city_options)
    if not chosen_city:
        return True  # Country was saved with default city

    if chosen_city == "MANUAL":
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.write(f"{BOLD}Enter City Name:{RESET} ")
        sys.stdout.flush()
        c_name = input().strip()
        if c_name:
            cfg["city"] = c_name
    else:
        cfg["city"] = chosen_city[0].split(" (")[0]
        cfg["latitude"] = chosen_city[1]
        cfg["longitude"] = chosen_city[2]

    return True


def choose_timezone(cfg):
    """Sub-menu to choose timezone."""
    # Get current system timezone
    system_tz = "Africa/Cairo"
    try:
        import time as pytime
        system_tz = pytime.tzname[0]
        # Or read /etc/timezone or /etc/localtime symlink
        if os.path.exists("/etc/timezone"):
            with open("/etc/timezone") as f:
                system_tz = f.read().strip()
        elif os.path.islink("/etc/localtime"):
            target = os.readlink("/etc/localtime")
            parts = target.split("zoneinfo/")
            if len(parts) > 1:
                system_tz = parts[1]
    except Exception:
        pass

    tz_options = [
        (f"Use Current System Timezone ({system_tz})", system_tz)
    ]
    for tz in COMMON_TIMEZONES:
        if tz != system_tz:
            tz_options.append((tz, tz))
    tz_options.append(("Enter Timezone Manually...", "MANUAL"))

    chosen = select_menu("Select Timezone", tz_options)
    if not chosen:
        return False

    if chosen == "MANUAL":
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.write(f"{BOLD}Enter Timezone (e.g. Africa/Cairo):{RESET} ")
        sys.stdout.flush()
        tz_in = input().strip()
        if tz_in:
            cfg["timezone"] = tz_in
            return True
        return False

    cfg["timezone"] = chosen
    return True


def choose_method(cfg):
    """Sub-menu to choose prayer calculation method."""
    method_options = []
    for k, v in CALCULATION_METHODS.items():
        method_options.append((f"{k}: {v}", k))

    chosen = select_menu("Select Calculation Method", method_options, initial_index=cfg.get("method", 5) - 1)
    if chosen is not None:
        cfg["method"] = chosen
        return True
    return False


def choose_duration(cfg):
    """Sub-menu to choose pause duration."""
    dur_options = [
        ("Single Pause (مرة واحدة) - Instant pause only", 0),
        ("Hold for 5 minutes (5 دقائق)", 5),
        ("Hold for 10 minutes (10 دقائق)", 10),
        ("Hold for 15 minutes (15 دقيقة)", 15),
        ("Hold for 20 minutes (20 دقيقة)", 20),
        ("Custom Duration in minutes...", -1),
    ]

    chosen = select_menu("Select Pause Duration", dur_options)
    if chosen is None:
        return False

    if chosen == -1:
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.write(f"{BOLD}Enter duration in minutes (0 for single pause):{RESET} ")
        sys.stdout.flush()
        val = input().strip()
        try:
            cfg["pause_duration_minutes"] = max(0, int(val))
            return True
        except ValueError:
            return False

    cfg["pause_duration_minutes"] = chosen
    return True


def run_config_tui():
    """Main Interactive TUI loop."""
    if not sys.stdin.isatty():
        cfg = load_config()
        print(json.dumps(cfg, indent=2, ensure_ascii=False))
        return

    cfg = load_config()
    modified = False

    while True:
        # Display main dashboard menu
        method_name = CALCULATION_METHODS.get(cfg.get("method", 5), "Custom")
        dur = cfg.get("pause_duration_minutes", 0)
        dur_str = "Single Pause (مرة واحدة)" if dur == 0 else f"{dur} minutes"
        notify_str = "Enabled (مفعّل)" if cfg.get("notifications", True) else "Disabled (معطل)"

        menu_title = (
            f"Tcalm Configuration Dashboard\n"
            f"  {DIM}Location:  {cfg.get('city')}, {cfg.get('country')}\n"
            f"  Timezone:  {cfg.get('timezone')}\n"
            f"  Method:    {method_name}\n"
            f"  Pause:     {dur_str}\n"
            f"  Notify:    {notify_str}{RESET}"
        )

        main_options = [
            ("Select Country & City (اختيار الدولة والمدينة)", "COUNTRY"),
            ("Detect Location & Timezone Automatically (كشف تلقائي بالـ IP)", "AUTO"),
            ("Change Timezone (تغيير المنطقة الزمنية)", "TIMEZONE"),
            ("Change Calculation Method (تغيير طريقة الحساب)", "METHOD"),
            ("Change Pause Duration (تغيير مدة الإيقاف)", "DURATION"),
            (f"Toggle Desktop Notifications (إشعارات: {notify_str})", "NOTIFICATIONS"),
            ("Save & Exit (حفظ وتطبيق)", "SAVE"),
            ("Cancel & Exit (إلغاء)", "EXIT")
        ]

        action = select_menu(menu_title, main_options)

        if action == "COUNTRY":
            if choose_country_and_city(cfg):
                modified = True

        elif action == "AUTO":
            sys.stdout.write(CLEAR_SCREEN)
            print(f"{BLUE}[*] Detecting location and timezone via IP...{RESET}")
            detected = detect_location()
            cfg.update(detected)
            modified = True
            print(f"{GREEN}[✓] Detected: {cfg.get('city')}, {cfg.get('country')} ({cfg.get('timezone')}){RESET}")
            print(f"\nPress Enter to continue...")
            read_key()

        elif action == "TIMEZONE":
            if choose_timezone(cfg):
                modified = True

        elif action == "METHOD":
            if choose_method(cfg):
                modified = True

        elif action == "DURATION":
            if choose_duration(cfg):
                modified = True

        elif action == "NOTIFICATIONS":
            cfg["notifications"] = not cfg.get("notifications", True)
            modified = True

        elif action == "SAVE":
            save_config(cfg)
            if os.path.exists(CACHE_FILE):
                try:
                    os.remove(CACHE_FILE)
                except Exception:
                    pass

            sys.stdout.write(CLEAR_SCREEN)
            print(f"{GREEN}[✓] Configuration saved successfully to ~/.config/tcalm/config.json{RESET}")

            # Restart running daemon if active
            pid = get_daemon_pid()
            if pid:
                print(f"{BLUE}[*] Restarting background daemon (PID: {pid}) to apply changes...{RESET}")
                try:
                    from tcalm_core.cli import cmd_restart
                    cmd_restart()
                except Exception:
                    pass

            print("\nDone.")
            break

        elif action in ("EXIT", None):
            sys.stdout.write(CLEAR_SCREEN)
            print("Configuration unchanged.")
            break
