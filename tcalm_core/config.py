import os
import json
from datetime import datetime
from tcalm_core.constants import CONFIG_DIR, CONFIG_FILE, LOG_FILE, DEFAULT_CONFIG
from tcalm_core.geo import detect_location


def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)


def log_message(msg):
    ensure_config_dir()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{now_str}] {msg}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted)
    except Exception:
        pass


def load_config():
    ensure_config_dir()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                merged = DEFAULT_CONFIG.copy()
                merged.update(cfg)
                return merged
        except Exception:
            pass

    # If no config exists, auto-detect and save
    cfg = detect_location()
    save_config(cfg)
    return cfg


def save_config(cfg):
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
