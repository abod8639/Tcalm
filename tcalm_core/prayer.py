import os
import math
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, date
from tcalm_core.constants import VERSION, CACHE_FILE
from tcalm_core.config import ensure_config_dir


def calculate_offline_prayer_times(lat, lng, tz_offset, calc_date=None, method=5):
    """Fallback offline astronomical calculation of prayer times."""
    if calc_date is None:
        calc_date = date.today()

    day_of_year = calc_date.timetuple().tm_yday
    b = 2 * math.pi * (day_of_year - 81) / 365
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    declination = 23.45 * math.sin(math.radians(360 / 365 * (day_of_year - 81)))
    solar_noon = 12 + (tz_offset * 15 - lng) / 15 - (eot / 60)

    def hour_angle(angle):
        rad_lat = math.radians(lat)
        rad_dec = math.radians(declination)
        rad_ang = math.radians(angle)
        cos_ha = (math.sin(rad_ang) - math.sin(rad_lat) * math.sin(rad_dec)) / (math.cos(rad_lat) * math.cos(rad_dec))
        if cos_ha > 1:
            return 0.0
        if cos_ha < -1:
            return 180.0
        return math.degrees(math.acos(cos_ha))

    fajr_angle = -19.5 if method == 5 else (-18.5 if method == 4 else -18.0)
    isha_angle = -17.5 if method == 5 else (-19.0 if method == 4 else -17.0)

    ha_fajr = hour_angle(fajr_angle) / 15.0
    ha_maghrib = hour_angle(-0.833) / 15.0
    ha_isha = hour_angle(isha_angle) / 15.0

    asr_alt = math.degrees(math.atan(1 / (1 + math.tan(math.radians(abs(lat - declination))))))
    ha_asr = hour_angle(asr_alt) / 15.0

    def format_h(h):
        h = h % 24
        hh = int(h)
        mm = int(round((h - hh) * 60))
        if mm == 60:
            hh = (hh + 1) % 24
            mm = 0
        return f"{hh:02d}:{mm:02d}"

    return {
        "Fajr": format_h(solar_noon - ha_fajr),
        "Dhuhr": format_h(solar_noon),
        "Asr": format_h(solar_noon + ha_asr),
        "Maghrib": format_h(solar_noon + ha_maghrib),
        "Isha": format_h(solar_noon + ha_isha)
    }


def get_prayer_times(cfg, target_date=None):
    """Fetch prayer times from Aladhan API with caching and offline fallback."""
    if target_date is None:
        target_date = date.today()

    date_str = target_date.strftime("%d-%m-%Y")
    cache_key = f"{date_str}_{cfg.get('city')}_{cfg.get('country')}_{cfg.get('method')}"

    # Check cache
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
                if cache_key in cache:
                    return cache[cache_key]
        except Exception:
            pass

    # Online fetch from Aladhan API
    city = urllib.parse.quote(str(cfg.get("city", "Cairo")))
    country = urllib.parse.quote(str(cfg.get("country", "Egypt")))
    method = cfg.get("method", 5)
    lat = cfg.get("latitude", 30.0444)
    lng = cfg.get("longitude", 31.2357)

    urls = [
        f"https://api.aladhan.com/v1/timingsByCity/{date_str}?city={city}&country={country}&method={method}",
        f"https://api.aladhan.com/v1/timings/{date_str}?latitude={lat}&longitude={lng}&method={method}"
    ]

    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"Tcalm/{VERSION}"})
            with urllib.request.urlopen(req, timeout=5) as res:
                data = json.loads(res.read().decode("utf-8"))
                if data.get("code") == 200 and "data" in data:
                    t = data["data"]["timings"]
                    timings = {
                        "Fajr": t["Fajr"].split(" ")[0],
                        "Dhuhr": t["Dhuhr"].split(" ")[0],
                        "Asr": t["Asr"].split(" ")[0],
                        "Maghrib": t["Maghrib"].split(" ")[0],
                        "Isha": t["Isha"].split(" ")[0]
                    }
                    cache[cache_key] = timings
                    ensure_config_dir()
                    try:
                        with open(CACHE_FILE, "w", encoding="utf-8") as f:
                            json.dump(cache, f, indent=2)
                    except Exception:
                        pass
                    return timings
        except Exception:
            continue

    # Fallback to local astronomical calculation
    tz_offset = datetime.now().astimezone().utcoffset().total_seconds() / 3600.0
    return calculate_offline_prayer_times(lat, lng, tz_offset, target_date, method)
