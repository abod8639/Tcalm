#!/usr/bin/env bash
# ==============================================================================
# Tcalm - Uninstaller Script
# ==============================================================================

set -e

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

echo -e "${YELLOW}Stopping Tcalm daemon if running...${NC}"
if command -v tcalm &> /dev/null; then
    tcalm stop || true
fi

INSTALL_BIN="$HOME/.local/bin/tcalm"
if [ -f "$INSTALL_BIN" ]; then
    rm -f "$INSTALL_BIN"
    echo -e "${GREEN}[✓] Removed $INSTALL_BIN${NC}"
fi

# Stop and remove systemd service if exists
SERVICE_FILE="$HOME/.config/systemd/user/tcalm.service"
if [ -f "$SERVICE_FILE" ]; then
    systemctl --user stop tcalm 2>/dev/null || true
    systemctl --user disable tcalm 2>/dev/null || true
    rm -f "$SERVICE_FILE"
    systemctl --user daemon-reload || true
    echo -e "${GREEN}[✓] Removed systemd user service${NC}"
fi

if [[ "$1" == "--purge" ]]; then
    rm -rf "$HOME/.config/tcalm"
    echo -e "${GREEN}[✓] Purged configuration and logs (~/.config/tcalm)${NC}"
else
    echo -e "${YELLOW}[i] Configuration kept at ~/.config/tcalm. Pass --purge to delete it.${NC}"
fi

echo -e "${GREEN}[✓] Tcalm uninstalled successfully.${NC}"
