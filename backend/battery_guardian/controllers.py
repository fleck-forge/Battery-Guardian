"""Hardware controller adapters. All adapters are read-only in this release."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Controller:
    name: str
    description: str
    kind: str


def controller_for(battery: Path) -> Controller:
    """Classify controls exposed by this battery, without guessing mode semantics."""
    start = (battery / "charge_control_start_threshold").exists()
    stop = (battery / "charge_control_end_threshold").exists()
    if start and stop:
        return Controller("sysfs-thresholds", "Kernel charge threshold interface", "thresholds")
    if (battery / "charge_types").exists():
        return Controller("sysfs-presets", "Device supplied charging presets", "presets")
    return Controller("monitor-only", "No supported charging control detected", "monitoring")
