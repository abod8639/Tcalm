# Tcalm

[English](README.md) | [العربية](README.ar.md)

![Tcalm Screenshot](assets/image.jpg)


<p align="center">
  <a href="https://github.com/abod8639/Tcalm/actions/workflows/ci.yml"><img src="https://github.com/abod8639/Tcalm/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <!-- <a href="https://app.codecov.io/gh/abod8639/Tcalm"><img src="https://codecov.io/gh/abod8639/Tcalm/graph/badge.svg" alt="Codecov" /></a> -->
  <a href="https://aur.archlinux.org/packages/tcalm"><img src="https://img.shields.io/aur/version/tcalm" alt="AUR version" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" /></a>
</p>

أداة سطر أوامر (CLI) خفيفة وعالية الكفاءة تعمل على نظامي Linux و macOS، تقوم بمراقبة مواقيت الصلاة في الخلفية وإيقاف تشغيل الوسائط (صوت وفيديو) فور دخول وقت الأذان مع إرسال إشعار على سطح المكتب.

---

## المميزات

- **إيقاف تلقائي للوسائط**:
  - **Linux**: التحكم في مشغلات الوسائط والمتصفحات (Chrome, Firefox, Brave, Spotify, VLC, MPV...) عبر معيار MPRIS وأداة `playerctl`، مع دعم احتياطي مباشر لـ DBus.
  - **macOS**: تكامل مباشر عبر AppleScript لدعم مشغلات Apple Music, Spotify, QuickTime Player, ومتصفحات Safari, Chrome, Brave.
- **تحديد دقيق للموقع والمنطقة الزمنية**:
  - كشف تلقائي للدولة والمدينة والإحداثيات والمنطقة الزمنية باستخدام خدمات التحديد الجغرافي وتوقيت النظام المحلي.
- **التوافق التام مع التوقيت الصيفي والشتوي (DST)**:
  - التكيف التلقائي مع تغيرات التوقيت دون الحاجة لإعادة تشغيل الخدمة، مع تحديث الحسابات يومياً.
- **استهلاك منخفض للغاية للموارد (~0% CPU)**:
  - تعمل الخدمة كـ Daemon خفيف يعتمد على حساب الفارق الزمني حتى الصلاة التالية والدخول في وضع السكون الذكي (Smart Sleep)، مع استهلاك ذاكرة أقل من 30 ميجابايت.
- **إدارة شاملة عبر سطر الأوامر**:
  - أوامر واضحة للتشغيل، الإيقاف، فحص الحالة، استعراض مواقيت اليوم، وتخصيص الموقع ومدة الإيقاف.
- **حساب فلكي محلي (Offline Fallback)**:
  - نظام تخزين مؤقت محلي (Cache) مقترن بمعادلات فلكية دقيقة لضمان استمرار العمل عند انقطاع الاتصال بالإنترنت.
- **هيكلية برمجية معيارية**:
  - كود منظم بالكامل في حزمة برمجية مستقلة (`tcalm_core`) تعتمد فقط على مكتبة بايثون القياسية بدون أي اعتمادات خارجية (Zero External Dependencies).

---

## التثبيت

### مستخدمو Arch Linux (AUR)
```bash
yay -S tcalm
```

### باقي توزيعات Linux و macOS
```bash
curl -fsSL https://raw.githubusercontent.com/abod8639/Tcalm/main/install.sh | bash
```

<details>
<summary>التثبيت اليدوي</summary>

```bash
git clone https://github.com/abod8639/Tcalm.git
cd Tcalm
./install.sh
```
</details>

> **المتطلبات**: بايثون 3.8+ (وأداة `playerctl` على لينكس للتحكم في الوسائط).

تأكد من وجود المسار `~/.local/bin` ضمن متغير البيئة `PATH`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## الاستخدام

### تشغيل الأداة في الخلفية
```bash
tcalm start
```

### إيقاف الأداة
```bash
tcalm stop
```

### إعادة التشغيل
```bash
tcalm restart
```

### فحص الحالة وموعد الأذان القادم
```bash
tcalm status
```

مثال على المخرجات:
```text
==================================================
                 Tcalm Status                     
==================================================
  ● Status:           RUNNING (PID: 172135)
  ● Location:         Giza, Egypt
  ● Timezone:         Africa/Cairo (UTC+03:00, DST: Active)
  ● Coordinates:      Lat: 30.0046, Lng: 31.2044
  ● Method:           Egyptian General Authority of Survey
  ● Pause Action:     Single Pause
--------------------------------------------------
    Next Prayer: Dhuhr (الظهر) at 12:49 (in 7h 5m)
==================================================
```

### عرض جدول مواقيت الصلاة لليوم
```bash
tcalm list
```

مثال على المخرجات:
```text
Prayer Times for Giza, Egypt (2026-09-18):
--------------------------------------------------
 Prayer      | الصلاة       | Time      | Status   
--------------------------------------------------
 Fajr        | الفجر        | 05:14     | Passed
 Dhuhr       | الظهر        | 12:49     | in 7h 5m
 Asr         | العصر        | 16:19     | in 10h 35m
 Maghrib     | المغرب       | 18:57     | in 13h 13m
 Isha        | العشاء       | 20:15     | in 14h 31m
--------------------------------------------------
```

### اختبار إيقاف الوسائط والتنبيه
```bash
tcalm test
```

---

## الإعدادات

يمكن عرض الإعدادات وتعديلها عبر واجهة المستخدم الطرفية التفاعلية (TUI) أو مباشرة عبر أعلام سطر الأوامر:

| الأمر | الوصف |
| :--- | :--- |
| `tcalm config` | فتح واجهة طرفية تفاعلية (TUI) لاختيار الدولة والمدينة والمنطقة الزمنية بالأسهم |
| `tcalm config --json` | عرض ملف الإعدادات الحالي بصيغة JSON بدون تشغيل الواجهة التفاعلية |
| `tcalm config --auto-detect` | إعادة الكشف التلقائي للموقع والمنطقة الزمنية عبر IP |
| `tcalm config --city "Alexandria"` | تحديد اسم المدينة يدوياً |
| `tcalm config --country "Egypt"` | تحديد اسم الدولة يدوياً |
| `tcalm config --timezone "Africa/Cairo"` | تحديد المنطقة الزمنية يدوياً |
| `tcalm config --lat 30.0444 --lng 31.2357` | تحديد الإحداثيات الجغرافية يدوياً |
| `tcalm config --duration 10` | إبقاء الوسائط موقوفة لمدة 10 دقائق (افتراضياً `0` للإيقاف لمرة واحدة) |
| `tcalm config --before 1` | إيقاف الوسائط قبل الأذان بـ N دقيقة (افتراضياً `1`، وضع `0` للإيقاف عند الأذان تماماً) |
| `tcalm config --method 5` | طريقة الحساب (1: كراتشي، 2: ISNA، 3: رابطة العالم الإسلامي، 4: أم القرى، 5: الهيئة المصرية) |
| `tcalm config --notifications false` | تعطيل إشعارات سطح المكتب (`true` للتفعيل) |

عند تعديل أي إعداد، يتم تطبيق التغييرات وإعادة تشغيل الخدمة تلقائياً في حال كانت تعمل في الخلفية.

---

لمتابعة حالة الخدمة أو مراجعة السجلات:
```bash
systemctl --user status tcalm
journalctl --user -u tcalm -f
```

---

## هيكلية المشروع

تعتمد الأداة على هيكلية برمجية معيارية تفصل كل وظيفة في وحدة مستقلة:

```text
Tcalm/
├── tcalm                        # نقطة الدخول التنفيذية لسطر الأوامر (< 35 سطر)
├── tcalm_core/                  # الحزمة البرمجية الأساسية
│   ├── constants.py             # الثوابت، المسارات، وطرق الحساب الفلكي
│   ├── config.py                # إدارة الإعدادات وملفات السجلات
│   ├── geo.py                   # كشف الموقع والمنطقة الزمنية عبر IP
│   ├── prayer.py                # الحساب الفلكي المحلي وواجهة Aladhan API
│   ├── media.py                 # التحكم بالوسائط وإرسال التنبيهات (Linux/macOS)
│   ├── daemon.py                # إدارة الـ Daemon في الخلفية والنوم الذكي
│   ├── cli.py                   # محلل المدخلات وأوامر سطر الأوامر
│   ├── __init__.py              # تعريف الحزمة ورقم الإصدار
│   └── __main__.py              # دعم التشغيل المباشر للحزمة
├── install.sh                   # سكربت التثبيت للنظام
├── uninstall.sh                 # سكربت إزالة التثبيت بالكامل
├── tcalm.service                # ملف تعريف خدمة systemd للمستخدم
├── README.md                    # التوثيق باللغة الإنجليزية
└── README.ar.md                 # التوثيق باللغة العربية
```

---

## إزالة التثبيت

### مستخدمو Arch Linux (AUR)
```bash
yay -R tcalm
```

### باقي توزيعات Linux و macOS
```bash
curl -fsSL https://raw.githubusercontent.com/abod8639/Tcalm/main/uninstall.sh | bash
```


---

## الترخيص

مرخص تحت رخصة MIT.
