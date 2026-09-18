import os

VERSION = "1.0.0"

CONFIG_DIR = os.path.expanduser("~/.config/tcalm")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
PID_FILE = os.path.join(CONFIG_DIR, "tcalm.pid")
LOG_FILE = os.path.join(CONFIG_DIR, "tcalm.log")
CACHE_FILE = os.path.join(CONFIG_DIR, "cache.json")

PRAYER_NAMES_AR = {
    "Fajr": "الفجر",
    "Dhuhr": "الظهر",
    "Asr": "العصر",
    "Maghrib": "المغرب",
    "Isha": "العشاء"
}

CALCULATION_METHODS = {
    1: "University of Islamic Sciences, Karachi",
    2: "Islamic Society of North America (ISNA)",
    3: "Muslim World League (MWL)",
    4: "Umm Al-Qura University, Makkah",
    5: "Egyptian General Authority of Survey",
    7: "Institute of Geophysics, University of Tehran",
    8: "Gulf Region",
    9: "Kuwait",
    10: "Qatar",
    11: "Majlis Ugama Islam Singapura",
    12: "Union des Organisations Islamiques de France",
    13: "Diyanet İşleri Başkanlığı, Turkey",
    14: "Spiritual Administration of Muslims of Russia",
    15: "Moonsighting Committee Worldwide"
}

DEFAULT_CONFIG = {
    "language": "en",
    "auto_detect": True,
    "city": "Cairo",
    "country": "Egypt",
    "latitude": 30.0444,
    "longitude": 31.2357,
    "timezone": "Africa/Cairo",
    "method": 5,
    "pause_duration_minutes": 0,
    "notifications": True,
    "prayers": ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
}
