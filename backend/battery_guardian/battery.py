"""Read battery and AC state from Linux power_supply sysfs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .capabilities import inspect_capabilities
from .controllers import controller_for


@dataclass(frozen=True)
class BatterySnapshot:
    available: bool
    battery_name: str | None
    percentage: int | None
    status: str
    ac_connected: bool | None
    capability: dict[str, Any]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return None


def _integer(text: str | None) -> int | None:
    try:
        return int(text) if text is not None else None
    except ValueError:
        return None


def discover_batteries(root: Path = Path("/sys/class/power_supply")) -> list[Path]:
    """Find batteries by their runtime sysfs `type`, without assuming BAT0."""
    try:
        entries = sorted(root.iterdir())
    except OSError:
        return []
    return [entry for entry in entries if _read(entry / "type") == "Battery"]


def read_snapshot(root: Path = Path("/sys/class/power_supply")) -> BatterySnapshot:
    batteries = discover_batteries(root)
    ac_values: list[bool] = []
    try:
        supplies = list(root.iterdir())
    except OSError:
        supplies = []
    for supply in supplies:
        if _read(supply / "type") in {"Mains", "USB", "USB_C"}:
            online = _integer(_read(supply / "online"))
            if online is not None:
                ac_values.append(online == 1)

    if not batteries:
        return BatterySnapshot(False, None, None, "Unavailable", any(ac_values) if ac_values else None,
                               {"level": "monitoring_only", "label": "Monitoring only",
                                "thresholds_supported": False, "modes": [], "thresholds": None},
                               "No battery was found in the power_supply interface.")

    # A primary battery is sufficient for the panel; controller detection uses its own capabilities.
    battery = batteries[0]
    present = _read(battery / "present")
    if present == "0":
        return BatterySnapshot(False, battery.name, None, "Unavailable", any(ac_values) if ac_values else None,
                               {"level": "monitoring_only", "label": "Monitoring only",
                                "thresholds_supported": False, "modes": [], "thresholds": None},
                               "The battery interface reports no battery present.")

    controller = controller_for(battery)
    capability = inspect_capabilities(battery, controller)
    percentage = _integer(_read(battery / "capacity"))
    if percentage is not None:
        percentage = min(100, max(0, percentage))
    status = _read(battery / "status") or "Unknown"
    return BatterySnapshot(True, battery.name, percentage, status,
                           any(ac_values) if ac_values else None, capability)
