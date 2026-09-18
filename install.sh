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
mkdir -p "$INSTALL_DIR"

SCRIPT_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/tcalm"

if [ ! -f "$SCRIPT_SRC" ]; then
    echo -e "${RED}[!] Error: Could not find 'tcalm' script in $(dirname "${BASH_SOURCE[0]}")${NC}"
    exit 1
fi

chmod +x "$SCRIPT_SRC"
cp "$SCRIPT_SRC" "$INSTALL_DIR/tcalm"

echo -e "${GREEN}[✓] Copied 'tcalm' to $INSTALL_DIR/tcalm${NC}"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}[!] Notice: $INSTALL_DIR is not in your current PATH.${NC}"
    echo -e "    Add it by running:"
    echo -e "      echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc (or ~/.zshrc)"
    echo -e "      source ~/.bashrc"
fi

# Optional systemd user service setup on Linux
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
    systemctl --user daemon-reload || true
    echo -e "${GREEN}[✓] Created systemd user service at $SERVICE_DIR/tcalm.service${NC}"
    echo -e "    You can enable it to start on boot: systemctl --user enable --now tcalm"
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
