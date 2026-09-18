import json
import urllib.request
import urllib.error
from tcalm_core.constants import VERSION, DEFAULT_CONFIG


def detect_location():
    """Detect country, city, coordinates and timezone via public IP services."""
    cfg = DEFAULT_CONFIG.copy()

    endpoints = [
        ("http://ip-api.com/json/", "ip-api"),
        ("https://ipwho.is/", "ipwhois")
    ]

    for url, service in endpoints:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"Tcalm/{VERSION}"})
            with urllib.request.urlopen(req, timeout=4) as res:
                data = json.loads(res.read().decode("utf-8"))

                if service == "ip-api" and data.get("status") == "success":
                    cfg["city"] = data.get("city", cfg["city"])
                    cfg["country"] = data.get("country", cfg["country"])
                    cfg["latitude"] = float(data.get("lat", cfg["latitude"]))
                    cfg["longitude"] = float(data.get("lon", cfg["longitude"]))
                    cfg["timezone"] = data.get("timezone", cfg["timezone"])
                    cfg["auto_detect"] = True
                    break
                elif service == "ipwhois" and data.get("success"):
                    cfg["city"] = data.get("city", cfg["city"])
                    cfg["country"] = data.get("country", cfg["country"])
                    cfg["latitude"] = float(data.get("latitude", cfg["latitude"]))
                    cfg["longitude"] = float(data.get("longitude", cfg["longitude"]))
                    tz = data.get("timezone", {})
                    if isinstance(tz, dict):
                        cfg["timezone"] = tz.get("id", cfg["timezone"])
                    cfg["auto_detect"] = True
                    break
        except Exception:
            continue

    # Auto-adjust calculation method based on country
    country_lower = cfg.get("country", "").lower()
    if "egypt" in country_lower:
        cfg["method"] = 5
    elif any(c in country_lower for c in ["saudi", "makkah", "arabia"]):
        cfg["method"] = 4
    elif any(c in country_lower for c in ["emirates", "uae", "kuwait", "qatar", "oman", "bahrain"]):
        cfg["method"] = 8
    elif "turkey" in country_lower:
        cfg["method"] = 13
    elif any(c in country_lower for c in ["pakistan", "india", "bangladesh"]):
        cfg["method"] = 1
    elif any(c in country_lower for c in ["united states", "canada", "america"]):
        cfg["method"] = 2
    else:
        cfg["method"] = 3

    return cfg
