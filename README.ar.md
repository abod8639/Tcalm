# 🕌 Tcalm (Prayer Time Media Pauser)

أداة سطر أوامر (CLI) خفيفة وعالية الكفاءة تعمل على **Linux** و **macOS**، تقوم بمراقبة مواقيت الصلاة تلقائياً في الخلفية وإيقاف مقاطع الفيديو والصوتيات فور دخول وقت الأذان مع إرسال إشعار تنبيهي على سطح المكتب.

---

## ✨ المميزات (Features)

- 🎧 **إيقاف تلقائي للوسائط**:
  - على **Linux**: التحكم بجميع مشغلات الوسائط والمتصفحات (Chrome, Firefox, Brave, Spotify, VLC, MPV...) عبر معيار MPRIS / `playerctl`.
  - على **macOS**: التحكم عبر AppleScript لمشغلات Apple Music, Spotify, QuickTime, والمتصفحات (Safari, Chrome, Brave...).
- 🌍 **تحديد الموقع والمنطقة الزمنية بدقة**:
  - كشف تلقائي للدولة، المدينة، الإحداثيات والمنطقة الزمنية عبر IP Geolocation وتوقيت النظام المحلي.
- ⏰ **التوافق التلقائي مع التوقيت الصيفي والشتوي (DST)**:
  - الأداة متجاوبة بشكل كامل مع تغيرات التوقيت الصيفي/الشتوي تلقائياً وتحدث مواقيتها يومياً بحسب تاريخ اليوم والمنطقة الزمنية.
- ⚡ **استهلاك موارد شبه معدوم (0% CPU)**:
  - مصممة كـ Daemon خفيف يعتمد على حساب الفرق الزمني حتى الأذان القادم ثم الدخول في وضع سكون (Smart Sleep) دون استهلاك المعالج أو البطارية (< 30MB RAM).
- 🛠️ **تحكم مرن وكامل**:
  - أوامر واضحة لتشغيل، إيقاف، فحص حالة الأداة، أو تعديل المدينة/المنطقة الزمنية ومدة الإيقاف يدوياً في أي وقت.
- 📴 **حساب فلكي مدمج (Offline Fallback)**:
  - تخزين مؤقت محلي (Cache) ومعادلات فلكية مدمجة لحساب المواقيت بدقة حتى في حال انقطاع اتصال الإنترنت.

---

## 🚀 التثبيت السريع (Installation)

### 1. إعطاء الصلاحيات وتشغيل سكربت التثبيت:

```bash
chmod +x install.sh
./install.sh
```

يقوم السكربت بنسخ `tcalm` إلى `~/.local/bin/tcalm` والتأكد من توفر الأدوات المطلوبة وضبط الإعدادات تلقائياً.

*(ملاحظة لمستخدمي لينكس: يوصى بتوفر `playerctl` للتحكم الأمثل بالوسائط: `sudo pacman -S playerctl` على Arch أو `sudo apt install playerctl` على Ubuntu/Debian).*

---

## 📖 دليل الاستخدام (Usage Guide)

### 1. تشغيل الأداة في الخلفية (Start Daemon)
```bash
tcalm start
```

### 2. إيقاف الأداة تماماً (Stop Daemon)
```bash
tcalm stop
```

### 3. إعادة التشغيل (Restart Daemon)
```bash
tcalm restart
```

### 4. فحص الحالة وموعد الأذان القادم (Status)
```bash
tcalm status
```
**مثال على المخرجات:**
```text
==================================================
                 Tcalm Status                     
==================================================
  ● Status:           RUNNING (PID: 161950)
  ● Location:         Giza, Egypt
  ● Timezone:         Africa/Cairo (UTC+03:00, DST: Active (صيفي))
  ● Coordinates:      Lat: 30.0046, Lng: 31.2044
  ● Method:           Egyptian General Authority of Survey
  ● Pause Action:     Single Pause (مرة واحدة)
--------------------------------------------------
    Next Prayer: Dhuhr (الظهر) at 12:49 (in 7h 16m)
==================================================
```

### 5. عرض جدول مواقيت الصلاة لليوم (List Timings)
```bash
tcalm list
```

### 6. تجربة فورية لإيقاف الوسائط والإشعار (Test)
```bash
tcalm test
```

---

## ⚙️ تخصيص الإعدادات (Configuration)

يمكنك عرض الإعدادات الحالية أو تعديلها بسهولة عبر أمر `tcalm config`:

| الأمر | الوصف |
| :--- | :--- |
| `tcalm config` | عرض ملف الإعدادات الحالي بصيغة JSON |
| `tcalm config --auto-detect` | إعادة الكشف التلقائي للموقع والمنطقة الزمنية عبر الـ IP |
| `tcalm config --city "Alexandria"` | تغيير المدينة يدوياً |
| `tcalm config --country "Egypt"` | تغيير الدولة يدوياً |
| `tcalm config --timezone "Africa/Cairo"` | تغيير المنطقة الزمنية |
| `tcalm config --duration 10` | إبقاء الوسائط موقوفة لمدة 10 دقائق أثناء الأذان والصلاة (افتراضياً `0` = إيقاف لمرة واحدة) |
| `tcalm config --method 5` | تغيير طريقة الحساب (1: كراتشي، 2: أمريكا الشمالية، 3: رابطة العالم الإسلامي، 4: أم القرى، 5: الهيئة المصرية العامة للمساحة) |
| `tcalm config --notifications false` | تعطيل إشعارات سطح المكتب (أو `true` لتفعيلها) |

*(ملاحظة: عند تعديل أي إعداد، يتم تطبيق التغييرات وإعادة تشغيل الخدمة في الخلفية تلقائياً).*

---

## 🐧 التشغيل التلقائي مع بدء النظام (Systemd Service - Linux)

إذا كنت ترغب بتشغيل الأداة تلقائياً عند تسجيل الدخول للنظام (مثل Arch Linux / Hyprland):

```bash
systemctl --user enable --now tcalm
```

وللتحقق من حالة الخدمة أو إيقافها:
```bash
systemctl --user status tcalm
systemctl --user stop tcalm
```

---

## 🏗️ هيكلية المشروع (Project Architecture)

تم تصميم الأداة بهيكلية برمجية معيارية (Modular Architecture) تلتزم بمبدأ المسؤولية الواحدة (Single Responsibility Principle) وبدون أي اعتمادات خارجية (Zero External Dependencies):

```text
Tcalm/
├── tcalm                        # نقطة الدخول التنفيذية الخفيفة
├── tcalm_core/                  # الحزمة البرمجية الأساسية
│   ├── constants.py             # الثوابت، المسارات الافتراضية، وطرق الحساب
│   ├── config.py                # إدارة ملفات الإعدادات والـ Logs
│   ├── geo.py                   # كشف الموقع الجغرافي والمنطقة الزمنية عبر IP
│   ├── prayer.py                # الحساب الفلكي المحلي وواجهة Aladhan API مع Caching
│   ├── media.py                 # التحكم بالوسائط وإرسال التنبيهات (Linux/macOS)
│   ├── daemon.py                # إدارة الـ Daemon في الخلفية والنوم الذكي
│   └── cli.py                   # واجهة الأوامر ومعالجة المدخلات (Argparse)
├── install.sh                   # سكربت التثبيت التلقائي للنظام
├── uninstall.sh                 # سكربت إزالة التثبيت بالكامل
└── tcalm.service                # ملف خدمة systemd للمستخدم
```

---

## 🗑️ إزالة التثبيت (Uninstallation)

لإزالة الأداة بالكامل:
```bash
chmod +x uninstall.sh
./uninstall.sh

# لحذف ملفات الإعدادات والسجلات المؤقتة أيضاً:
./uninstall.sh --purge
```
