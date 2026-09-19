#!/usr/bin/env bash
# ==============================================================================
# Tcalm - Installer Script for Linux & macOS
# ==============================================================================

set -e

GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

echo -e "${BLUE}==============================================${NC}"
echo -e "${BLUE}        Tcalm Installer (Linux & macOS)        ${NC}"
echo -e "${BLUE}==============================================${NC}"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python 3 is required but not installed.${NC}"
    echo -e "    Please install Python 3 and try again."
    exit 1
fi

OS="$(uname -s)"
if [ "$OS" = "Linux" ]; then
    echo -e "${GREEN}[*] Detected OS: Linux${NC}"
    if ! command -v playerctl &> /dev/null; then
        echo -e "${YELLOW}[!] Note: 'playerctl' is recommended for pausing media on Linux.${NC}"
        echo -e "    Install it via: sudo pacman -S playerctl (Arch) or sudo apt install playerctl (Ubuntu/Debian)"
    else
        echo -e "${GREEN}[✓] playerctl is installed.${NC}"
    fi
elif [ "$OS" = "Darwin" ]; then
    echo -e "${GREEN}[*] Detected OS: macOS${NC}"
else
    echo -e "${YELLOW}[!] Warning: Unsupported OS: $OS. Tcalm is designed for Linux and macOS.${NC}"
fi

# Determine install location
INSTALL_DIR="$HOME/.local/bin"
SHARE_DIR="$HOME/.local/share/tcalm"
mkdir -p "$INSTALL_DIR" "$SHARE_DIR"

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || echo "")"
SCRIPT_SRC="$SRC_DIR/tcalm"
MODULES_SRC="$SRC_DIR/tcalm_core"

TEMP_DIR=""
if [ -z "$SRC_DIR" ] || [ ! -f "$SCRIPT_SRC" ] || [ ! -d "$MODULES_SRC" ]; then
    echo -e "${BLUE}[*] Fetching Tcalm repository...${NC}"
    TEMP_DIR="$(mktemp -d)"
    trap 'rm -rf "$TEMP_DIR"' EXIT
    git clone --depth 1 https://github.com/abod8639/Tcalm.git "$TEMP_DIR" &> /dev/null || {
        echo -e "${RED}[!] Error: Failed to clone repository from GitHub.${NC}"
        exit 1
    }
    SRC_DIR="$TEMP_DIR"
    SCRIPT_SRC="$SRC_DIR/tcalm"
    MODULES_SRC="$SRC_DIR/tcalm_core"
fi

chmod +x "$SCRIPT_SRC"
rm -rf "$SHARE_DIR/tcalm_core"
cp -r "$MODULES_SRC" "$SHARE_DIR/"
cp "$SCRIPT_SRC" "$INSTALL_DIR/tcalm"
chmod +x "$INSTALL_DIR/tcalm"

if [ -f "$SRC_DIR/uninstall.sh" ]; then
    cp "$SRC_DIR/uninstall.sh" "$SHARE_DIR/uninstall.sh"
    chmod +x "$SHARE_DIR/uninstall.sh"
fi

echo -e "${GREEN}[✓] Installed 'tcalm_core' to $SHARE_DIR${NC}"
echo -e "${GREEN}[✓] Installed 'tcalm' binary to $INSTALL_DIR/tcalm${NC}"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}[!] Notice: $INSTALL_DIR is not in your current PATH.${NC}"
    echo -e "    Add it by running:"
    echo -e "      echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc (or ~/.zshrc)"
    echo -e "      source ~/.bashrc"
fi

# Systemd user service setup on Linux
if [ "$OS" = "Linux" ] && command -v systemctl &> /dev/null; then
    SERVICE_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SERVICE_DIR"
    
    cat <<EOF > "$SERVICE_DIR/tcalm.service"
[Unit]
Description=Tcalm - Prayer Time Media Pauser
After=network.target sound.target

[Service]
Type=simple
ExecStart=$INSTALL_DIR/tcalm run
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF
    systemctl --user daemon-reload 2>/dev/null || true
    if systemctl --user enable --now tcalm 2>/dev/null; then
        systemctl --user restart tcalm 2>/dev/null || true
        echo -e "${GREEN}[✓] Enabled and started systemd user service (tcalm)${NC}"
        sleep 0.5
    else
        echo -e "${GREEN}[✓] Created systemd user service at $SERVICE_DIR/tcalm.service${NC}"
        echo -e "${YELLOW}[!] Notice: Could not automatically start systemd service (no active user session).${NC}"
        echo -e "    You can enable and start it manually: systemctl --user enable --now tcalm"
    fi
fi

echo -e "\n${BLUE}Initializing configuration & checking status...${NC}"
"$INSTALL_DIR/tcalm" status || true

echo -e "\n${GREEN}==============================================${NC}"
echo -e "${GREEN}       Installation Complete Successfully!     ${NC}"
echo -e "${GREEN}==============================================${NC}"
echo -e "Commands you can use:"
echo -e "  ${YELLOW}tcalm start${NC}     - Start background daemon"
echo -e "  ${YELLOW}tcalm stop${NC}      - Stop background daemon"
echo -e "  ${YELLOW}tcalm status${NC}    - Show status and next prayer"
echo -e "  ${YELLOW}tcalm list${NC}      - List today's prayer times"
echo -e "  ${YELLOW}tcalm test${NC}      - Test media pausing & notification"
echo -e "  ${YELLOW}tcalm config${NC}    - View or modify settings"
