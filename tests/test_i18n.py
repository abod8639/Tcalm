import pytest
from tcalm_core.i18n import (
    t,
    get_prayer_name,
    get_method_name,
    LANGUAGES,
    PRAYER_NAMES,
)


def test_languages_dict():
    assert "ar" in LANGUAGES
    assert "en" in LANGUAGES


def test_prayer_name_localization():
    assert get_prayer_name("Fajr", lang="ar") == "الفجر"
    assert get_prayer_name("Fajr", lang="en") == "Fajr"
    assert get_prayer_name("Maghrib", lang="ar") == "المغرب"
    assert get_prayer_name("UnknownPrayer", lang="ar") == "UnknownPrayer"


def test_method_name_localization():
    method_ar = get_method_name(5, lang="ar")
    method_en = get_method_name(5, lang="en")
    assert "المصرية" in method_ar
    assert "Egyptian" in method_en


def test_translation_formatting():
    msg_ar = t("notify_title", lang="ar", prayer="العصر")
    assert "العصر" in msg_ar
    msg_en = t("notify_title", lang="en", prayer="Asr")
    assert "Asr" in msg_en

    # Fallback to key if not found
    assert t("non_existent_key_xyz", lang="en") == "non_existent_key_xyz"

    # Pre-adhan translation tests
    before_1m_ar = t("notify_title_before_1m", lang="ar", prayer="الظهر")
    assert "الظهر" in before_1m_ar and "متبقي دقيقة" in before_1m_ar
    before_1m_en = t("notify_title_before_1m", lang="en", prayer="Dhuhr")
    assert "Dhuhr" in before_1m_en and "1 minute" in before_1m_en

