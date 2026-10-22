#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -m pip install --user "$ROOT[service]"
mkdir -p "$HOME/.config/systemd/user" "$HOME/.local/share/dbus-1/services"
install -m 0644 "$ROOT/systemd/battery-guardian.service" "$HOME/.config/systemd/user/"
install -m 0644 "$ROOT/systemd/org.batteryguardian.Service.service" "$HOME/.local/share/dbus-1/services/"
systemctl --user daemon-reload
systemctl --user enable --now battery-guardian.service

EXT_DIR="$HOME/.local/share/gnome-shell/extensions/battery-guardian@batteryguardian.org"
mkdir -p "$EXT_DIR"
install -m 0644 "$ROOT"/gnome-extension/* "$EXT_DIR/"
gnome-extensions enable battery-guardian@batteryguardian.org || true
printf '%s\n' 'Installed for the current user. Log out and back in if the extension is not visible.'
