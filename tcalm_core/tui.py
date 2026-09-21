import os
import sys
import json
import tty
import termios
import select

from tcalm_core.constants import CACHE_FILE
from tcalm_core.config import load_config, save_config
from tcalm_core.geo import detect_location
from tcalm_core.daemon import get_daemon_pid
from tcalm_core.i18n import (
    LANGUAGES,
    CALCULATION_METHODS,
    t,
    get_method_name,
)

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
        "country_ar": "مصر",
        "country_en": "Egypt",
        "method": 5,
        "timezone": "Africa/Cairo",
        "lat": 30.0444, "lng": 31.2357,
        "cities": [
            {"ar": "القاهرة", "en": "Cairo", "lat": 30.0444, "lng": 31.2357},
            {"ar": "الإسكندرية", "en": "Alexandria", "lat": 31.2001, "lng": 29.9187},
            {"ar": "الجيزة", "en": "Giza", "lat": 30.0131, "lng": 31.2089},
            {"ar": "المنصورة", "en": "Mansoura", "lat": 31.0409, "lng": 31.3785},
            {"ar": "طنطا", "en": "Tanta", "lat": 30.7865, "lng": 31.0004},
            {"ar": "أسيوط", "en": "Assiut", "lat": 27.1783, "lng": 31.1859},
            {"ar": "سوهاج", "en": "Sohag", "lat": 26.5569, "lng": 31.6948},
            {"ar": "الأقصر", "en": "Luxor", "lat": 25.6872, "lng": 32.6396},
            {"ar": "أسوان", "en": "Aswan", "lat": 24.0889, "lng": 32.8998},
            {"ar": "بورسعيد", "en": "Port Said", "lat": 31.2653, "lng": 32.3019},
            {"ar": "السويس", "en": "Suez", "lat": 29.9668, "lng": 32.5498},
            {"ar": "الغردقة", "en": "Hurghada", "lat": 27.2579, "lng": 33.8116},
            {"ar": "شرم الشيخ", "en": "Sharm El-Sheikh", "lat": 27.9158, "lng": 34.3299},
        ]
    },
    {
        "country_ar": "المملكة العربية السعودية",
        "country_en": "Saudi Arabia",
        "method": 4,
        "timezone": "Asia/Riyadh",
        "lat": 24.7136, "lng": 46.6753,
        "cities": [
            {"ar": "مكة المكرمة", "en": "Makkah", "lat": 21.3891, "lng": 39.8579},
            {"ar": "المدينة المنورة", "en": "Madinah", "lat": 24.5247, "lng": 39.5692},
            {"ar": "الرياض", "en": "Riyadh", "lat": 24.7136, "lng": 46.6753},
            {"ar": "جدة", "en": "Jeddah", "lat": 21.5433, "lng": 39.1728},
            {"ar": "الدمام", "en": "Dammam", "lat": 26.4207, "lng": 50.0888},
            {"ar": "الخبر", "en": "Khobar", "lat": 26.2172, "lng": 50.1971},
            {"ar": "الطائف", "en": "Taif", "lat": 21.2854, "lng": 40.4222},
            {"ar": "تبوك", "en": "Tabuk", "lat": 28.3835, "lng": 36.5662},
            {"ar": "أبها", "en": "Abha", "lat": 18.2164, "lng": 42.5053},
            {"ar": "بريدة", "en": "Buraidah", "lat": 26.3260, "lng": 43.9750},
        ]
    },
    {
        "country_ar": "الإمارات العربية المتحدة",
        "country_en": "United Arab Emirates",
        "method": 8,
        "timezone": "Asia/Dubai",
        "lat": 25.2048, "lng": 55.2708,
        "cities": [
            {"ar": "أبوظبي", "en": "Abu Dhabi", "lat": 24.4539, "lng": 54.3773},
            {"ar": "دبي", "en": "Dubai", "lat": 25.2048, "lng": 55.2708},
            {"ar": "الشارقة", "en": "Sharjah", "lat": 25.3463, "lng": 55.4209},
            {"ar": "عجمان", "en": "Ajman", "lat": 25.4052, "lng": 55.5136},
            {"ar": "رأس الخيمة", "en": "Ras Al Khaimah", "lat": 25.7895, "lng": 55.9432},
            {"ar": "العين", "en": "Al Ain", "lat": 24.2075, "lng": 55.7447},
        ]
    },
    {
        "country_ar": "الكويت",
        "country_en": "Kuwait",
        "method": 9,
        "timezone": "Asia/Kuwait",
        "lat": 29.3759, "lng": 47.9774,
        "cities": [
            {"ar": "مدينة الكويت", "en": "Kuwait City", "lat": 29.3759, "lng": 47.9774},
            {"ar": "حولي", "en": "Hawalli", "lat": 29.3328, "lng": 48.0282},
            {"ar": "السالمية", "en": "Salmiya", "lat": 29.3344, "lng": 48.0772},
            {"ar": "الأحمدي", "en": "Ahmadi", "lat": 29.0769, "lng": 48.0839},
        ]
    },
    {
        "country_ar": "قطر",
        "country_en": "Qatar",
        "method": 10,
        "timezone": "Asia/Qatar",
        "lat": 25.2854, "lng": 51.5310,
        "cities": [
            {"ar": "الدوحة", "en": "Doha", "lat": 25.2854, "lng": 51.5310},
            {"ar": "الريان", "en": "Al Rayyan", "lat": 25.2919, "lng": 51.4244},
            {"ar": "الوكرة", "en": "Al Wakrah", "lat": 25.1768, "lng": 51.6048},
        ]
    },
    {
        "country_ar": "البحرين",
        "country_en": "Bahrain",
        "method": 8,
        "timezone": "Asia/Bahrain",
        "lat": 26.2285, "lng": 50.5860,
        "cities": [
            {"ar": "المنامة", "en": "Manama", "lat": 26.2285, "lng": 50.5860},
            {"ar": "الرفاع", "en": "Riffa", "lat": 26.1300, "lng": 50.5550},
            {"ar": "المحرق", "en": "Muharraq", "lat": 26.2572, "lng": 50.6119},
        ]
    },
    {
        "country_ar": "سلطنة عمان",
        "country_en": "Oman",
        "method": 8,
        "timezone": "Asia/Muscat",
        "lat": 23.5880, "lng": 58.3829,
        "cities": [
            {"ar": "مسقط", "en": "Muscat", "lat": 23.5880, "lng": 58.3829},
            {"ar": "صلالة", "en": "Salalah", "lat": 17.0151, "lng": 54.0924},
            {"ar": "صحار", "en": "Sohar", "lat": 24.3461, "lng": 56.7075},
            {"ar": "نزوى", "en": "Nizwa", "lat": 22.9333, "lng": 57.5333},
        ]
    },
    {
        "country_ar": "الأردن",
        "country_en": "Jordan",
        "method": 3,
        "timezone": "Asia/Amman",
        "lat": 31.9454, "lng": 35.9284,
        "cities": [
            {"ar": "عمّان", "en": "Amman", "lat": 31.9454, "lng": 35.9284},
            {"ar": "الزرقاء", "en": "Zarqa", "lat": 32.0728, "lng": 36.0880},
            {"ar": "إربد", "en": "Irbid", "lat": 32.5568, "lng": 35.8469},
            {"ar": "العقبة", "en": "Aqaba", "lat": 29.5321, "lng": 35.0063},
        ]
    },
    {
        "country_ar": "فلسطين",
        "country_en": "Palestine",
        "method": 3,
        "timezone": "Asia/Gaza",
        "lat": 31.9522, "lng": 35.2332,
        "cities": [
            {"ar": "القدس الشريف", "en": "Jerusalem", "lat": 31.7683, "lng": 35.2137},
            {"ar": "غزة", "en": "Gaza", "lat": 31.5017, "lng": 34.4668},
            {"ar": "رام الله", "en": "Ramallah", "lat": 31.9038, "lng": 35.2034},
            {"ar": "نابلس", "en": "Nablus", "lat": 32.2211, "lng": 35.2544},
            {"ar": "الخليل", "en": "Hebron", "lat": 31.5326, "lng": 35.0998},
        ]
    },
    {
        "country_ar": "العراق",
        "country_en": "Iraq",
        "method": 3,
        "timezone": "Asia/Baghdad",
        "lat": 33.3152, "lng": 44.3661,
        "cities": [
            {"ar": "بغداد", "en": "Baghdad", "lat": 33.3152, "lng": 44.3661},
            {"ar": "البصرة", "en": "Basra", "lat": 30.5081, "lng": 47.7835},
            {"ar": "أربيل", "en": "Erbil", "lat": 36.1911, "lng": 44.0092},
            {"ar": "الموصل", "en": "Mosul", "lat": 36.3400, "lng": 43.1300},
            {"ar": "النجف الأشرف", "en": "Najaf", "lat": 32.0259, "lng": 44.3462},
        ]
    },
    {
        "country_ar": "المغرب",
        "country_en": "Morocco",
        "method": 3,
        "timezone": "Africa/Casablanca",
        "lat": 33.5731, "lng": -7.5898,
        "cities": [
            {"ar": "الدار البيضاء", "en": "Casablanca", "lat": 33.5731, "lng": -7.5898},
            {"ar": "الرباط", "en": "Rabat", "lat": 34.0209, "lng": -6.8416},
            {"ar": "مراكش", "en": "Marrakech", "lat": 31.6295, "lng": -7.9811},
            {"ar": "فاس", "en": "Fes", "lat": 34.0331, "lng": -5.0003},
            {"ar": "طنجة", "en": "Tangier", "lat": 35.7595, "lng": -5.8340},
        ]
    },
    {
        "country_ar": "الجزائر",
        "country_en": "Algeria",
        "method": 3,
        "timezone": "Africa/Algiers",
        "lat": 36.7538, "lng": 3.0588,
        "cities": [
            {"ar": "الجزائر العاصمة", "en": "Algiers", "lat": 36.7538, "lng": 3.0588},
            {"ar": "وهران", "en": "Oran", "lat": 35.6987, "lng": -0.6349},
            {"ar": "قسنطينة", "en": "Constantine", "lat": 36.3650, "lng": 6.6147},
        ]
    },
    {
        "country_ar": "تونس",
        "country_en": "Tunisia",
        "method": 3,
        "timezone": "Africa/Tunis",
        "lat": 36.8065, "lng": 10.1815,
        "cities": [
            {"ar": "تونس العاصمة", "en": "Tunis", "lat": 36.8065, "lng": 10.1815},
            {"ar": "صفاقس", "en": "Sfax", "lat": 34.7406, "lng": 10.7603},
            {"ar": "سوسة", "en": "Sousse", "lat": 35.8256, "lng": 10.6369},
        ]
    },
    {
        "country_ar": "تركيا",
        "country_en": "Turkey",
        "method": 13,
        "timezone": "Europe/Istanbul",
        "lat": 41.0082, "lng": 28.9784,
        "cities": [
            {"ar": "إسطنبول", "en": "Istanbul", "lat": 41.0082, "lng": 28.9784},
            {"ar": "أنقرة", "en": "Ankara", "lat": 39.9334, "lng": 32.8597},
            {"ar": "إزمير", "en": "Izmir", "lat": 38.4237, "lng": 27.1428},
            {"ar": "بورصة", "en": "Bursa", "lat": 40.1828, "lng": 29.0667},
            {"ar": "أنطاليا", "en": "Antalya", "lat": 36.8969, "lng": 30.7133},
        ]
    },
    {
        "country_ar": "المملكة المتحدة",
        "country_en": "United Kingdom",
        "method": 3,
        "timezone": "Europe/London",
        "lat": 51.5074, "lng": -0.1278,
        "cities": [
            {"ar": "لندن", "en": "London", "lat": 51.5074, "lng": -0.1278},
            {"ar": "برمنغهام", "en": "Birmingham", "lat": 52.4862, "lng": -1.8904},
            {"ar": "مانشستر", "en": "Manchester", "lat": 53.4808, "lng": -2.2426},
        ]
    },
    {
        "country_ar": "الولايات المتحدة الأمريكية",
        "country_en": "United States",
        "method": 2,
        "timezone": "America/New_York",
        "lat": 40.7128, "lng": -74.0060,
        "cities": [
            {"ar": "نيويورك", "en": "New York", "lat": 40.7128, "lng": -74.0060},
            {"ar": "شيكاغو", "en": "Chicago", "lat": 41.8781, "lng": -87.6298},
            {"ar": "لوس أنجلوس", "en": "Los Angeles", "lat": 34.0522, "lng": -118.2437},
            {"ar": "هيوستن", "en": "Houston", "lat": 29.7604, "lng": -95.3698},
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
    """Reads a single keypress or ANSI escape sequence using unbuffered os.read."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        b = os.read(fd, 1)
        if not b:
            return None

        if b == b'\x1b':
            # Check if more bytes of an escape sequence are waiting in the OS buffer
            r, _, _ = select.select([fd], [], [], 0.05)
            if not r:
                return 'ESC'
            seq = os.read(fd, 31)
            full = b + seq

            if full in (b'\x1b[A', b'\x1bOA') or (full.startswith((b'\x1b[', b'\x1bO')) and full.endswith(b'A')):
                return 'UP'
            elif full in (b'\x1b[B', b'\x1bOB') or (full.startswith((b'\x1b[', b'\x1bO')) and full.endswith(b'B')):
                return 'DOWN'
            elif full in (b'\x1b[C', b'\x1bOC') or (full.startswith((b'\x1b[', b'\x1bO')) and full.endswith(b'C')):
                return 'RIGHT'
            elif full in (b'\x1b[D', b'\x1bOD') or (full.startswith((b'\x1b[', b'\x1bO')) and full.endswith(b'D')):
                return 'LEFT'
            elif b'3~' in full:
                return 'BACKSPACE'
            elif full in (b'\x1b[H', b'\x1b[1~'):
                return 'HOME'
            elif full in (b'\x1b[F', b'\x1b[4~'):
                return 'END'
            elif b'5~' in full:
                return 'PAGE_UP'
            elif b'6~' in full:
                return 'PAGE_DOWN'
            return 'ESC'

        if b in (b'\r', b'\n'):
            return 'ENTER'
        elif b in (b'\x7f', b'\x08'):
            return 'BACKSPACE'
        elif b == b'\x03':  # Ctrl+C
            raise KeyboardInterrupt

        # Multi-byte UTF-8 handling for non-ASCII input (e.g. Arabic characters)
        lead = b[0]
        if lead < 0x80:
            return b.decode('utf-8', errors='ignore')
        elif (lead & 0xE0) == 0xC0:
            needed = 1
        elif (lead & 0xF0) == 0xE0:
            needed = 2
        elif (lead & 0xF8) == 0xF0:
            needed = 3
        else:
            needed = 0

        if needed > 0:
            rem = os.read(fd, needed)
            return (b + rem).decode('utf-8', errors='ignore')

        return b.decode('utf-8', errors='ignore')
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def select_menu(title, options, initial_index=0, lang="en", start_search=False):
    """
    Renders an interactive selection list navigable with UP/DOWN arrows.
    Supports pressing '/' to activate instant live search / filtering.
    """
    selected = initial_index
    page_size = 12
    offset = 0
    search_query = ""
    search_mode = start_search

    num_total = len(options)
    if num_total == 0:
        return None

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    try:
        while True:
            # Filter options based on search query
            if search_query.strip():
                q = search_query.strip().lower()
                filtered_options = []
                for opt in options:
                    label = opt[0] if isinstance(opt, tuple) else str(opt)
                    val = opt[1] if isinstance(opt, tuple) else opt
                    matched = q in label.lower()
                    if not matched and isinstance(val, dict):
                        matched = (
                            q in val.get("country_ar", "").lower()
                            or q in val.get("country_en", "").lower()
                            or q in val.get("ar", "").lower()
                            or q in val.get("en", "").lower()
                        )
                    if not matched and isinstance(val, str):
                        matched = q in val.lower()
                    if matched:
                        filtered_options.append(opt)
            else:
                filtered_options = list(options)

            num_items = len(filtered_options)
            if num_items > 0 and selected >= num_items:
                selected = num_items - 1

            if selected < offset:
                offset = selected
            elif selected >= offset + page_size:
                offset = selected - page_size + 1

            lines = [CLEAR_SCREEN]
            lines.append(f"{BOLD}{BLUE}=================================================={RESET}")
            lines.append(f"  {BOLD}{title}{RESET}")
            lines.append(f"{BOLD}{BLUE}=================================================={RESET}")
            lines.append(f"{DIM}{t('tui_nav_help', lang=lang)}{RESET}\n")

            if search_mode or search_query:
                lines.append(f"  {YELLOW}{t('tui_search_prompt', lang=lang)}:{RESET} {BOLD}{search_query}{RESET}█\n")

            if num_items == 0:
                lines.append(f"  {DIM}{t('tui_no_results', lang=lang)}{RESET}\n")
            else:
                visible_items = filtered_options[offset:offset + page_size]
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
            if not key:
                continue

            if key == '/':
                search_mode = True
                continue
            elif search_mode and key == 'BACKSPACE':
                if search_query:
                    search_query = search_query[:-1]
                selected = 0
                offset = 0
                continue
            elif key == 'UP':
                if num_items > 0:
                    selected = (selected - 1) % num_items
            elif key == 'DOWN':
                if num_items > 0:
                    selected = (selected + 1) % num_items
            elif key in ('PAGE_UP',):
                if num_items > 0:
                    selected = max(0, selected - page_size)
            elif key in ('PAGE_DOWN',):
                if num_items > 0:
                    selected = min(num_items - 1, selected + page_size)
            elif key == 'ENTER':
                if num_items > 0:
                    chosen = filtered_options[selected]
                    return chosen[1] if isinstance(chosen, tuple) else chosen
            elif search_mode and len(key) == 1 and key.isprintable():
                search_query += key
                selected = 0
                offset = 0
                continue
            elif key in ('ESC', 'q', 'Q'):
                if search_query:
                    search_query = ""
                    selected = 0
                    offset = 0
                    continue
                elif search_mode:
                    search_mode = False
                    continue
                else:
                    return None
    finally:
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()


def choose_country_and_city(cfg):
    """Wizard to select country and corresponding city in pure chosen language."""
    lang = cfg.get("language", "en")
    country_field = "country_ar" if lang == "ar" else "country_en"
    city_field = "ar" if lang == "ar" else "en"

    country_options = [(c[country_field], c) for c in COUNTRIES_DATA]
    country_options.append((t("tui_custom_entry", lang=lang), "CUSTOM"))

    chosen_country = select_menu(
        t("tui_select_country", lang=lang),
        country_options,
        lang=lang
    )
    if not chosen_country:
        return False

    if chosen_country == "CUSTOM":
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.write(f"{BOLD}{t('tui_enter_country', lang=lang)}{RESET} ")
        sys.stdout.flush()
        c_name = input().strip()
        if not c_name:
            return False
        sys.stdout.write(f"{BOLD}{t('tui_enter_city', lang=lang)}{RESET} ")
        sys.stdout.flush()
        city_name = input().strip()
        if not city_name:
            return False

        cfg["country"] = c_name
        cfg["city"] = city_name
        cfg["auto_detect"] = False
        return True

    cfg["country"] = chosen_country[country_field]
    cfg["method"] = chosen_country["method"]
    cfg["timezone"] = chosen_country["timezone"]
    cfg["latitude"] = chosen_country["lat"]
    cfg["longitude"] = chosen_country["lng"]
    cfg["auto_detect"] = False

    # Choose city
    city_options = [(c[city_field], c) for c in chosen_country["cities"]]
    city_options.append((t("tui_custom_entry", lang=lang), "MANUAL"))

    title = t("tui_select_city", lang=lang, country=chosen_country[country_field])
    chosen_city = select_menu(title, city_options, lang=lang)
    if not chosen_city:
        return True

    if chosen_city == "MANUAL":
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.write(f"{BOLD}{t('tui_enter_city', lang=lang)}{RESET} ")
        sys.stdout.flush()
        c_name = input().strip()
        if c_name:
            cfg["city"] = c_name
    else:
        cfg["city"] = chosen_city[city_field]
        cfg["latitude"] = chosen_city["lat"]
        cfg["longitude"] = chosen_city["lng"]

    return True


def choose_timezone(cfg):
    """Sub-menu to choose timezone in chosen language."""
    lang = cfg.get("language", "en")
    system_tz = "Africa/Cairo"
    try:
        import time as pytime
        system_tz = pytime.tzname[0]
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
        (t("tui_system_tz", lang=lang, tz=system_tz), system_tz)
    ]
    for tz_val in COMMON_TIMEZONES:
        if tz_val != system_tz:
            tz_options.append((tz_val, tz_val))
    tz_options.append((t("tui_custom_entry", lang=lang), "MANUAL"))

    chosen = select_menu(t("tui_select_timezone", lang=lang), tz_options, lang=lang)
    if not chosen:
        return False

    if chosen == "MANUAL":
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.write(f"{BOLD}{t('tui_enter_timezone', lang=lang)}{RESET} ")
        sys.stdout.flush()
        tz_in = input().strip()
        if tz_in:
            cfg["timezone"] = tz_in
            return True
        return False

    cfg["timezone"] = chosen
    return True


def choose_method(cfg):
    """Sub-menu to choose prayer calculation method in chosen language."""
    lang = cfg.get("language", "en")
    methods_dict = CALCULATION_METHODS.get(lang, CALCULATION_METHODS["ar"])
    method_options = []
    for k, v in methods_dict.items():
        method_options.append((f"{k}: {v}", k))

    chosen = select_menu(
        t("tui_select_method", lang=lang),
        method_options,
        initial_index=max(0, cfg.get("method", 5) - 1),
        lang=lang
    )
    if chosen is not None:
        cfg["method"] = chosen
        return True
    return False


def choose_duration(cfg):
    """Sub-menu to choose pause duration in chosen language."""
    lang = cfg.get("language", "en")
    dur_options = [
        (t("single_pause", lang=lang), 0),
        (t("hold_minutes", lang=lang, minutes=5), 5),
        (t("hold_minutes", lang=lang, minutes=10), 10),
        (t("hold_minutes", lang=lang, minutes=15), 15),
        (t("hold_minutes", lang=lang, minutes=20), 20),
        (t("tui_custom_entry", lang=lang), -1),
    ]

    chosen = select_menu(t("tui_select_duration", lang=lang), dur_options, lang=lang)
    if chosen is None:
        return False

    if chosen == -1:
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.write(f"{BOLD}{t('tui_enter_duration', lang=lang)}{RESET} ")
        sys.stdout.flush()
        val = input().strip()
        try:
            cfg["pause_duration_minutes"] = max(0, int(val))
            return True
        except ValueError:
            return False

    cfg["pause_duration_minutes"] = chosen
    return True


def choose_pause_before(cfg):
    """Sub-menu to choose pre-adhan pause timing in chosen language."""
    lang = cfg.get("language", "en")
    before_options = [
        (t("pause_before_1m", lang=lang), 1),
        (t("pause_before_exact", lang=lang), 0),
        (t("pause_before_nm", lang=lang, minutes=2), 2),
        (t("pause_before_nm", lang=lang, minutes=3), 3),
        (t("pause_before_nm", lang=lang, minutes=5), 5),
        (t("tui_custom_entry", lang=lang), -1),
    ]

    chosen = select_menu(t("tui_select_pause_before", lang=lang), before_options, lang=lang)
    if chosen is None:
        return False

    if chosen == -1:
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.write(f"{BOLD}{t('tui_enter_pause_before', lang=lang)}{RESET} ")
        sys.stdout.flush()
        val = input().strip()
        try:
            cfg["pause_before_minutes"] = max(0, int(val))
            return True
        except ValueError:
            return False

    cfg["pause_before_minutes"] = chosen
    return True


def choose_language(cfg):
    """Sub-menu to choose application language (Arabic or English)."""
    lang = cfg.get("language", "en")
    lang_options = [
        ("العربية (Arabic)", "ar"),
        ("English (الإنجليزية)", "en")
    ]
    chosen = select_menu("اختر لغة الواجهة / Select Language", lang_options, lang=lang)
    if chosen:
        cfg["language"] = chosen
        return True
    return False


def run_config_tui():
    """Main Interactive TUI loop in pure chosen language."""
    if not sys.stdin.isatty():
        cfg = load_config()
        print(json.dumps(cfg, indent=2, ensure_ascii=False))
        return

    cfg = load_config()

    while True:
        lang = cfg.get("language", "en")
        method_name = get_method_name(cfg.get("method", 5), lang=lang)
        dur = cfg.get("pause_duration_minutes", 0)
        dur_str = t("single_pause", lang=lang) if dur == 0 else t("hold_minutes", lang=lang, minutes=dur)
        pause_before = cfg.get("pause_before_minutes", 1)
        if pause_before == 0:
            before_str = t("pause_before_exact", lang=lang)
        elif pause_before == 1:
            before_str = t("pause_before_1m", lang=lang)
        else:
            before_str = t("pause_before_nm", lang=lang, minutes=pause_before)
        notify_str = t("tui_enabled", lang=lang) if cfg.get("notifications", True) else t("tui_disabled", lang=lang)
        current_lang_name = LANGUAGES.get(lang, "English")

        menu_title = (
            f"{t('tui_dashboard', lang=lang)}\n"
            f"  {DIM}{t('location', lang=lang)}:  {cfg.get('city')}, {cfg.get('country')}\n"
            f"  {t('timezone', lang=lang)}:  {cfg.get('timezone')}\n"
            f"  {t('method', lang=lang)}:    {method_name}\n"
            f"  {t('pause_action', lang=lang)}: {dur_str}\n"
            f"  {t('pause_before', lang=lang)}: {before_str}\n"
            f"  {t('tui_opt_notify', lang=lang, status=notify_str)}{RESET}"
        )

        main_options = [
            (f"{t('tui_opt_language', lang=lang)}: {BOLD}{current_lang_name}{RESET}", "LANGUAGE"),
            (t("tui_opt_country", lang=lang), "COUNTRY"),
            (t("tui_opt_auto", lang=lang), "AUTO"),
            (t("tui_opt_timezone", lang=lang), "TIMEZONE"),
            (t("tui_opt_method", lang=lang), "METHOD"),
            (t("tui_opt_duration", lang=lang), "DURATION"),
            (t("tui_opt_pause_before", lang=lang), "PAUSE_BEFORE"),
            (t("tui_opt_notify", lang=lang, status=notify_str), "NOTIFICATIONS"),
            (t("tui_opt_save", lang=lang), "SAVE"),
            (t("tui_opt_cancel", lang=lang), "EXIT")
        ]

        action = select_menu(menu_title, main_options, lang=lang)

        if action == "LANGUAGE":
            choose_language(cfg)

        elif action == "COUNTRY":
            choose_country_and_city(cfg)

        elif action == "AUTO":
            sys.stdout.write(CLEAR_SCREEN)
            print(f"{BLUE}{t('auto_detecting', lang=lang)}{RESET}")
            detected = detect_location()
            cfg.update(detected)
            print(f"{GREEN}{t('auto_detected', lang=lang, city=cfg.get('city'), country=cfg.get('country'), timezone=cfg.get('timezone'))}{RESET}")
            print(f"\nPress Enter / اضغط Enter للمتابعة...")
            read_key()

        elif action == "TIMEZONE":
            choose_timezone(cfg)

        elif action == "METHOD":
            choose_method(cfg)

        elif action == "DURATION":
            choose_duration(cfg)

        elif action == "PAUSE_BEFORE":
            choose_pause_before(cfg)

        elif action == "NOTIFICATIONS":
            cfg["notifications"] = not cfg.get("notifications", True)

        elif action == "SAVE":
            save_config(cfg)
            if os.path.exists(CACHE_FILE):
                try:
                    os.remove(CACHE_FILE)
                except Exception:
                    pass

            sys.stdout.write(CLEAR_SCREEN)
            print(f"{GREEN}{t('tui_saved_msg', lang=lang)} ~/.config/tcalm/config.json{RESET}")

            pid = get_daemon_pid()
            if pid:
                print(f"{BLUE}{t('tui_restarting_msg', lang=lang)}{RESET}")
                try:
                    from tcalm_core.cli import cmd_restart
                    cmd_restart()
                except Exception:
                    pass
            break

        elif action in ("EXIT", None):
            sys.stdout.write(CLEAR_SCREEN)
            print(t("tui_unchanged_msg", lang=lang))
            break
