# Battery Guardian

Battery Guardian is an open-source GNOME Shell panel extension and Python session service for Linux battery monitoring. It reports the battery state and the charging-control interfaces exposed by the running kernel. Hardware controls vary by laptop and firmware; threshold support is never assumed.

## Current scope

- Read-only battery percentage, status, AC connection, threshold values, and device-advertised charging modes.
- Capability labels: **Adjustable thresholds supported**, **Preset charging modes only**, or **Monitoring only**.
- GNOME Shell 42 extension, targeted at Pop!_OS 22.04.
- User-session D-Bus service and user-level systemd unit.
- Default desired thresholds are documented as 50% start and 100% stop. Threshold editing and hardware application are not enabled in this release.
- No root service, `sudo`, or arbitrary command execution.

On a device that exposes only `charge_types`, mode names and semantics remain device-defined. Battery Guardian reports them without interpreting or changing the active mode. It does not claim that a preset provides a particular charge range.

## Requirements

- Linux with `/sys/class/power_supply` (or run the backend against a compatible fixture in tests).
- Python 3.10 or newer; `dbus-next` is required for the service.
- GNOME Shell 42 for the included extension metadata and APIs.
- A user systemd session.

## Install for the current user

From the repository root:

```sh
./scripts/install-user.sh
```

The script installs the Python package, user D-Bus activation descriptor, user systemd unit, and extension. It enables the user service and GNOME extension. Log out and back in if GNOME Shell does not load the extension immediately. No charging settings are changed.

To remove the service and extension:

```sh
./scripts/uninstall-user.sh
```

The uninstall script leaves the JSON preferences in `~/.config/battery-guardian/config.json`.

## Development

```sh
python3 -m pip install -e '.[service,test]'
python3 -m pytest
```

When pytest is unavailable, run the included standard-library fallback:

```sh
PYTHONPATH=backend python3 backend/tests/run_tests.py
```

The test suite uses temporary directories as fake sysfs trees; it never writes to the host's actual battery interfaces. To run the service manually after installing the optional dependency:

```sh
battery-guardian-service
```

Logs go to stderr and can be adjusted with `BATTERY_GUARDIAN_LOG_LEVEL=DEBUG`.

## Interfaces and safety

The backend discovers battery devices by reading each power supply's `type`, and reads optional attributes only when present. It does not require a fixed battery name. Threshold validation requires integer values in `[0, 100]` with start strictly below stop. No current implementation writes threshold or preset attributes.

The controller abstraction (`backend/battery_guardian/controllers.py`) is the extension point for additional kernel or vendor-supported controls. A future write-capable controller must have a narrow, documented authorization boundary and explicit user action. Monitoring remains unprivileged.

## Contributing

Please add tests using temporary sysfs fixtures for every new capability. Do not infer control semantics from attribute names or preset labels. Document the exact hardware/kernel interface and permission model for any new controller.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
