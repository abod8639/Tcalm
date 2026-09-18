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

### 1. Requirements

- Python 3.8+
- Linux: `playerctl` (recommended for optimal media management)
  - Arch Linux: `sudo pacman -S playerctl`
  - Debian / Ubuntu: `sudo apt install playerctl`
  - Fedora: `sudo dnf install playerctl`
- macOS: macOS 10.15+ (no extra packages needed)

### 2. Install

#### One-Line Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/abot8639/Tcalm/master/install.sh | bash
```

Or using `wget`:
```bash
wget -qO- https://raw.githubusercontent.com/abot8639/Tcalm/master/install.sh | bash
```

#### Manual Installation

```bash
git clone https://github.com/abot8639/Tcalm.git
cd Tcalm
chmod +x install.sh
./install.sh
```

The installer performs the following:
1. Validates Python environment and dependencies.
2. Installs the `tcalm_core` package to `~/.local/share/tcalm`.
3. Installs the executable binary to `~/.local/bin/tcalm`.
4. (Linux) Configures a systemd user service unit (`tcalm.service`).

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

Settings can be inspected and updated using the `tcalm config` subcommand:

| Command | Description |
| :--- | :--- |
| `tcalm config` | Print current configuration in JSON format |
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

To remove Tcalm from your system:

```bash
chmod +x uninstall.sh
./uninstall.sh

# To purge configuration, cache, and log files (~/.config/tcalm):
./uninstall.sh --purge
```

---

## License

MIT License.
