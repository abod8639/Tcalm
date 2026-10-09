"""
Updater module for Tcalm.
Handles checking GitHub releases for newer versions.
"""

import json
import urllib.request
import urllib.error
from tcalm_core.constants import VERSION, GITHUB_REPO, GITHUB_API_LATEST_RELEASE
from tcalm_core.i18n import t


def parse_version(v_str):
    """
    Parses a version string (e.g. 'v1.1.0' or '1.2.3') into a tuple of ints.
    Returns e.g. (1, 1, 0).
    """
    if not v_str:
        return (0, 0, 0)
    clean = str(v_str).strip().lstrip("vV")
    parts = []
    for part in clean.split("."):
        digits = ""
        for ch in part:
            if ch.isdigit():
                digits += ch
            else:
                break
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def check_for_updates(timeout=3):
    """
    Checks GitHub releases for a newer version of Tcalm.
    Returns dict:
      {
        "has_update": bool,
        "current_version": str,
        "latest_version": str,
        "release_url": str,
        "error": Optional[str]
      }
    """
    current_tuple = parse_version(VERSION)
    try:
        req = urllib.request.Request(
            GITHUB_API_LATEST_RELEASE,
            headers={
                "User-Agent": f"Tcalm/{VERSION}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                tag_name = data.get("tag_name", "").strip()
                html_url = data.get("html_url", f"https://github.com/{GITHUB_REPO}/releases")
                latest_clean = tag_name.lstrip("vV")
                latest_tuple = parse_version(tag_name)
                has_update = latest_tuple > current_tuple
                return {
                    "has_update": has_update,
                    "current_version": VERSION,
                    "latest_version": latest_clean or VERSION,
                    "release_url": html_url,
                    "error": None
                }
    except Exception as e:
        return {
            "has_update": False,
            "current_version": VERSION,
            "latest_version": None,
            "release_url": None,
            "error": str(e)
        }

    return {
        "has_update": False,
        "current_version": VERSION,
        "latest_version": VERSION,
        "release_url": None,
        "error": None
    }


def cmd_version(cfg=None, check_update=True):
    """
    Displays the current version and optionally checks GitHub for updates.
    """
    lang = (cfg or {}).get("language", "en") if isinstance(cfg, dict) else "en"
    print(f"Tcalm version {VERSION}")

    if not check_update:
        return

    print(t("checking_updates", lang=lang))
    result = check_for_updates()

    if result.get("error"):
        print(t("update_check_failed", lang=lang))
    elif result.get("has_update"):
        print(t("update_available", lang=lang, latest=result["latest_version"], current=result["current_version"]))
        print(t("update_instructions", lang=lang))
    else:
        print(t("update_up_to_date", lang=lang, current=result["current_version"]))
