# Tcalm

[English](README.md) | [العربية](README.ar.md)

A lightweight, zero-dependency command-line utility for Linux and macOS that monitors Islamic prayer times (Adhan) in the background, automatically pausing media playback during prayer times and delivering desktop notifications.

---

## Features

- **Automatic Media Pausing**:
  - **Linux**: Controls active media players and browsers (Chrome, Firefox, Brave, Spotify, VLC, MPV, etc.) via the MPRIS D-Bus interface and `playerctl`.
  - **macOS**: Native AppleScript integration for Apple Music, Spotify, QuickTime Player, Safari, Chrome, and Brave.
- **Geolocation & Timezone Detection**:
  - Automatically resolves country, city, coordinates, and local timezone via public IP geolocation services and local system configuration.
- **Daylight Saving Time (DST) Handling**:
  - Fully responsive to seasonal clock changes (summer/winter time), dynamically recalculating timings daily without service restarts.
- **Low Resource Consumption (~0% CPU)**:
  - Runs as an efficient daemon with intelligent interval sleeping between prayers, keeping CPU utilization near zero and memory consumption under 30MB.
- **Comprehensive CLI**:
  - Commands to start, stop, query service status, list daily prayer schedules, and customize parameters.
- **Offline Astronomical Fallback**:
  - Local caching combined with built-in astronomical solar algorithms ensures prayer times remain accessible even when disconnected from the network.
- **Modular Package Structure**:
  - Clean separation of concerns (`tcalm_core`) relying exclusively on the Python standard library with no third-party package dependencies.

---

## Installation

### Arch Linux (AUR)
```bash
yay -S tcalm
```

### Linux & macOS
```bash
curl -fsSL https://raw.githubusercontent.com/abod8639/Tcalm/main/install.sh | bash
```

<details>
<summary>Manual Installation</summary>

```bash
git clone https://github.com/abod8639/Tcalm.git
cd Tcalm
./install.sh
```
</details>

> **Requirements**: Python 3.8+ (and `playerctl` on Linux for media control).

Ensure `~/.local/bin` is included in your system `PATH`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## Usage

### Start Daemon
```bash
tcalm start
```

### Stop Daemon
```bash
tcalm stop
```

### Restart Daemon
```bash
tcalm restart
```

### Service Status
```bash
tcalm status
```

Example output:
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

### Daily Timetable
```bash
tcalm list
```

Example output:
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

### Test Media Pause & Notification
```bash
tcalm test
```

---

## Configuration

Settings can be inspected and updated interactively via the built-in Terminal UI (TUI) or through direct CLI flags:

| Command | Description |
| :--- | :--- |
| `tcalm config` | Launch interactive Terminal UI (TUI) to configure country, city, timezone, etc. |
| `tcalm config --json` | Print current configuration in JSON format without TUI |
| `tcalm config --auto-detect` | Detect location and timezone automatically via IP |
| `tcalm config --city "Alexandria"` | Set city name |
| `tcalm config --country "Egypt"` | Set country name |
| `tcalm config --timezone "Africa/Cairo"` | Set timezone identifier |
| `tcalm config --lat 30.0444 --lng 31.2357` | Set custom geographic coordinates |
| `tcalm config --duration 10` | Hold playback pause for N minutes (default `0` for single pause) |
| `tcalm config --method 5` | Calculation method (1-15, e.g. 1: Karachi, 2: ISNA, 3: MWL, 4: Makkah, 5: Egypt) |
| `tcalm config --notifications false` | Toggle desktop notifications (`true` / `false`) |

Updating any configuration parameter automatically restarts running daemon processes to apply the changes.

---

## Systemd Service (Linux)

To enable automatic background execution on user login:

```bash
systemctl --user enable --now tcalm
```

To monitor service state or view logs:
```bash
systemctl --user status tcalm
journalctl --user -u tcalm -f
```

---

## Architecture

Tcalm follows a modular architecture adhering to the Single Responsibility Principle:

```text
Tcalm/
├── tcalm                        # Executable CLI entrypoint (< 35 lines)
├── tcalm_core/                  # Core package
│   ├── constants.py             # File paths, default configurations, calculation methods
│   ├── config.py                # Configuration management and logging
│   ├── geo.py                   # IP geolocation and timezone detection
│   ├── prayer.py                # Offline calculations and Aladhan API cache handler
│   ├── media.py                 # Media player controllers (Linux/macOS) and notifications
│   ├── daemon.py                # Background process loop and sleep scheduling
│   ├── cli.py                   # Argument parser and CLI subcommands
│   ├── __init__.py              # Package metadata and version definition
│   └── __main__.py              # Module execution support (`python3 -m tcalm_core`)
├── install.sh                   # Installation script
├── uninstall.sh                 # Removal script
├── tcalm.service                # Systemd user service unit definition
├── README.md                    # English documentation
└── README.ar.md                 # Arabic documentation
```

---

## Uninstallation

### Arch Linux (AUR)
```bash
yay -R tcalm
```

### Linux & macOS
```bash
curl -fsSL https://raw.githubusercontent.com/abod8639/Tcalm/main/uninstall.sh | bash
```

> **Clean Data**: To completely remove configuration, logs, and cache (`~/.config/tcalm`):
> ```bash
> rm -rf ~/.config/tcalm
> ```

---

## License

MIT License.
