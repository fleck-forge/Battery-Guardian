#!/usr/bin/env bash
set -euo pipefail
UUID=battery-guardian@batteryguardian.org
gnome-extensions disable "$UUID" || true
systemctl --user disable --now battery-guardian.service || true
rm -f "$HOME/.config/systemd/user/battery-guardian.service"
rm -f "$HOME/.local/share/dbus-1/services/org.batteryguardian.Service.service"
rm -rf "$HOME/.local/share/gnome-shell/extensions/$UUID"
systemctl --user daemon-reload
printf '%s\n' 'Removed the Battery Guardian service and extension. User preferences were preserved.'
