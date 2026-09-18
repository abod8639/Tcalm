"""
Internationalization (i18n) module for Tcalm.
Ensures pure Arabic or pure English interface without language mixing.
"""

LANGUAGES = {
    "ar": "العربية",
    "en": "English"
}

PRAYER_NAMES = {
    "ar": {
        "Fajr": "الفجر",
        "Dhuhr": "الظهر",
        "Asr": "العصر",
        "Maghrib": "المغرب",
        "Isha": "العشاء"
    },
    "en": {
        "Fajr": "Fajr",
        "Dhuhr": "Dhuhr",
        "Asr": "Asr",
        "Maghrib": "Maghrib",
        "Isha": "Isha"
    }
}

CALCULATION_METHODS = {
    "ar": {
        1: "جامعة العلوم الإسلامية، كراتشي",
        2: "الجمعية الإسلامية لأمريكا الشمالية (ISNA)",
        3: "رابطة العالم الإسلامي",
        4: "جامعة أم القرى، مكة المكرمة",
        5: "الهيئة المصرية العامة للمساحة",
        7: "معهد الجيوفيزياء، جامعة طهران",
        8: "منطقة الخليج العربي",
        9: "دولة الكويت",
        10: "دولة قطر",
        11: "مجلس الشؤون الإسلامية، سنغافورة",
        12: "اتحاد المنظمات الإسلامية بفرنسا",
        13: "رئاسة الشؤون الدينية، تركيا",
        14: "الإدارة الدينية لمسلمي روسيا",
        15: "لجنة رؤية الهلال العالمية"
    },
    "en": {
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
}

MESSAGES = {
    "ar": {
        "status_running": "يعمل",
        "status_stopped": "متوقف",
        "status_title": "حالة الأداة (Tcalm)",
        "location": "الموقع",
        "timezone": "المنطقة الزمنية",
        "dst_active": "مفعّل (توقيت صيفي)",
        "dst_inactive": "غير مفعّل (توقيت شتوي)",
        "coordinates": "الإحداثيات",
        "method": "طريقة الحساب",
        "pause_action": "إيقاف الوسائط",
        "single_pause": "إيقاف فوري لمرة واحدة",
        "hold_minutes": "إيقاف لمدة {minutes} دقيقة",
        "next_prayer": "الأذان القادم: {name} في {time} (متبقي {left})",
        "next_fajr_tomorrow": "الأذان القادم: الفجر غداً صباحاً.",
        "list_title": "جدول مواقيت الصلاة لمدينة {city}، {country} ({date}):",
        "col_prayer": "الصلاة",
        "col_time": "الوقت",
        "col_status": "الحالة",
        "status_passed": "انتهت",
        "status_in": "متبقي {time}",
        "time_hours_minutes": "{hours} س و {minutes} د",
        "time_minutes": "{minutes} دقيقة",
        "notify_title": "حان الآن موعد أذان {prayer}",
        "notify_body": "تم إيقاف تشغيل الوسائط مؤقتاً (Tcalm)",
        "test_start": "[*] جاري تجربة إيقاف الوسائط وإرسال التنبيه...",
        "test_paused": "[✓] تم تفعيل إيقاف الوسائط (النجاح: {success}).",
        "test_notified": "[✓] تم إرسال الإشعار، من المفترض ظهوره الآن على سطح المكتب.",
        "daemon_started": "[✓] تم تشغيل الخدمة في الخلفية بنجاح (المعرف: {pid}).",
        "daemon_already_running": "[*] الخدمة تعمل بالفعل في الخلفية (المعرف: {pid}).",
        "daemon_stopping": "[*] جاري إيقاف خدمة Tcalm (المعرف: {pid})...",
        "daemon_stopped": "[✓] تم إيقاف الخدمة بنجاح.",
        "daemon_not_running": "[-] الخدمة ليست قيد التشغيل حالياً.",
        "config_saved": "[✓] تم تحديث الإعدادات بنجاح.",
        "config_restarting": "[*] جاري إعادة تشغيل الخدمة لتطبيق التغييرات...",
        "auto_detecting": "[*] جاري كشف الموقع والمنطقة الزمنية تلقائياً...",
        "auto_detected": "[✓] تم الكشف بنجاح: {city}، {country} ({timezone})",
        "invalid_method": "[!] طريقة حساب غير صحيحة. اختر رقماً من 1 إلى 15.",
        "tui_dashboard": "لوحة تحكم إعدادات Tcalm",
        "tui_nav_help": "الأسهم [↑/↓] للتنقل، [/] للبحث، [Enter] للاختيار، [Esc] للرجوع",
        "tui_search_prompt": "بحث",
        "tui_no_results": "لا توجد نتائج مطابقة",
        "tui_opt_language": "لغة الواجهة (Language)",
        "tui_opt_country": "تحديد الدولة والمدينة",
        "tui_opt_auto": "كشف الموقع والمنطقة الزمنية تلقائياً (IP)",
        "tui_opt_timezone": "تحديد المنطقة الزمنية",
        "tui_opt_method": "تحديد طريقة الحساب الفلكي",
        "tui_opt_duration": "تحديد مدة إيقاف الوسائط",
        "tui_opt_notify": "إشعارات سطح المكتب: {status}",
        "tui_opt_save": "حفظ وتطبيق الإعدادات",
        "tui_opt_cancel": "إلغاء الخروج",
        "tui_enabled": "مفعلة",
        "tui_disabled": "معطلة",
        "tui_saved_msg": "[✓] تم حفظ الإعدادات بنجاح في",
        "tui_restarting_msg": "[*] جاري إعادة تشغيل الخدمة في الخلفية لتطبيق التعديلات...",
        "tui_unchanged_msg": "لم يتم تعديل الإعدادات.",
        "tui_select_country": "اختر الدولة",
        "tui_select_city": "اختر المدينة في {country}",
        "tui_select_timezone": "اختر المنطقة الزمنية",
        "tui_select_method": "اختر طريقة حساب المواقيت",
        "tui_select_duration": "اختر مدة إيقاف الوسائط",
        "tui_enter_country": "أدخل اسم الدولة:",
        "tui_enter_city": "أدخل اسم المدينة:",
        "tui_enter_timezone": "أدخل المنطقة الزمنية (مثال: Africa/Cairo):",
        "tui_enter_duration": "أدخل المدة بالدقائق (0 للإيقاف الفوري فقط):",
        "tui_custom_entry": "إدخال يدوي مخصص...",
        "tui_system_tz": "استخدام توقيت النظام المحلي ({tz})"
    },
    "en": {
        "status_running": "RUNNING",
        "status_stopped": "STOPPED",
        "status_title": "Tcalm Status",
        "location": "Location",
        "timezone": "Timezone",
        "dst_active": "Active (Summer DST)",
        "dst_inactive": "Inactive (Winter)",
        "coordinates": "Coordinates",
        "method": "Method",
        "pause_action": "Pause Action",
        "single_pause": "Single Pause (Instant)",
        "hold_minutes": "Hold for {minutes} minutes",
        "next_prayer": "Next Prayer: {name} at {time} (in {left})",
        "next_fajr_tomorrow": "Next Prayer: Fajr tomorrow morning.",
        "list_title": "Prayer Times for {city}, {country} ({date}):",
        "col_prayer": "Prayer",
        "col_time": "Time",
        "col_status": "Status",
        "status_passed": "Passed",
        "status_in": "in {time}",
        "time_hours_minutes": "{hours}h {minutes}m",
        "time_minutes": "{minutes}m",
        "notify_title": "It is now time for {prayer} prayer",
        "notify_body": "Media paused by Tcalm",
        "test_start": "[*] Testing media pause and desktop notification...",
        "test_paused": "[✓] Media pause triggered (Success: {success}).",
        "test_notified": "[✓] Notification sent. You should see a desktop banner.",
        "daemon_started": "[✓] Tcalm daemon started successfully (PID: {pid}).",
        "daemon_already_running": "[*] Tcalm is already running (PID: {pid}).",
        "daemon_stopping": "[*] Stopping Tcalm daemon (PID: {pid})...",
        "daemon_stopped": "[✓] Tcalm daemon stopped.",
        "daemon_not_running": "[-] Tcalm is not running.",
        "config_saved": "[✓] Configuration updated successfully.",
        "config_restarting": "[*] Restarting running daemon to apply changes...",
        "auto_detecting": "[*] Detecting location and timezone automatically...",
        "auto_detected": "[✓] Detected: {city}, {country} ({timezone})",
        "invalid_method": "[!] Invalid method. Choose from 1 to 15.",
        "tui_dashboard": "Tcalm Configuration Dashboard",
        "tui_nav_help": "Arrows [↑/↓] to navigate, [/] to search, [Enter] to select, [Esc] to return",
        "tui_search_prompt": "Search",
        "tui_no_results": "No matching results",
        "tui_opt_language": "Interface Language (اللغة)",
        "tui_opt_country": "Select Country & City",
        "tui_opt_auto": "Auto-Detect Location & Timezone via IP",
        "tui_opt_timezone": "Change Timezone",
        "tui_opt_method": "Change Calculation Method",
        "tui_opt_duration": "Change Pause Duration",
        "tui_opt_notify": "Desktop Notifications: {status}",
        "tui_opt_save": "Save & Apply Settings",
        "tui_opt_cancel": "Cancel & Exit",
        "tui_enabled": "Enabled",
        "tui_disabled": "Disabled",
        "tui_saved_msg": "[✓] Configuration saved successfully to",
        "tui_restarting_msg": "[*] Restarting background daemon to apply changes...",
        "tui_unchanged_msg": "Configuration unchanged.",
        "tui_select_country": "Select Country",
        "tui_select_city": "Select City in {country}",
        "tui_select_timezone": "Select Timezone",
        "tui_select_method": "Select Calculation Method",
        "tui_select_duration": "Select Pause Duration",
        "tui_enter_country": "Enter Country Name:",
        "tui_enter_city": "Enter City Name:",
        "tui_enter_timezone": "Enter Timezone (e.g. Africa/Cairo):",
        "tui_enter_duration": "Enter duration in minutes (0 for single pause):",
        "tui_custom_entry": "Manual / Custom Entry...",
        "tui_system_tz": "Use Current System Timezone ({tz})"
    }
}


def t(key, lang="ar", **kwargs):
    """Retrieve translated string by key and format with kwargs."""
    lang_msgs = MESSAGES.get(lang, MESSAGES["ar"])
    template = lang_msgs.get(key, MESSAGES["en"].get(key, key))
    if kwargs:
        return template.format(**kwargs)
    return template


def get_prayer_name(prayer_key, lang="ar"):
    """Returns localized prayer name."""
    names = PRAYER_NAMES.get(lang, PRAYER_NAMES["ar"])
    return names.get(prayer_key, prayer_key)


def get_method_name(method_id, lang="ar"):
    """Returns localized calculation method name."""
    methods = CALCULATION_METHODS.get(lang, CALCULATION_METHODS["ar"])
    return methods.get(method_id, f"Custom ({method_id})")
