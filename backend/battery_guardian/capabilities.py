"""Runtime capability discovery for Linux battery charge controls."""

from __future__ import annotations

from pathlib import Path

from .controllers import Controller


def available_modes(battery: Path) -> tuple[list[str], str | None]:
    """Return kernel-advertised choices and selected choice, preserving names."""
    try:
        tokens = (battery / "charge_types").read_text(encoding="utf-8").split()
    except (OSError, UnicodeError):
        return [], None
    selected: list[str] = []
    modes: list[str] = []
    for token in tokens:
        if token.startswith("[") and token.endswith("]"):
            selected.append(token[1:-1])
            modes.append(token[1:-1])
        else:
            modes.append(token)
    return modes, selected[0] if selected else None


def _threshold(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        value = int(path.read_text(encoding="utf-8").strip())
        return value if 0 <= value <= 100 else None
    except (OSError, ValueError, UnicodeError):
        return None


def inspect_capabilities(battery: Path, controller: Controller) -> dict[str, object]:
    start_path = battery / "charge_control_start_threshold"
    end_path = battery / "charge_control_end_threshold"
    start_exists, end_exists = start_path.exists(), end_path.exists()
    thresholds_supported = start_exists and end_exists
    modes, active = available_modes(battery)
    if thresholds_supported:
        level, label = "thresholds", "Adjustable thresholds supported"
    elif modes:
        level, label = "presets", "Preset charging modes only"
    else:
        level, label = "monitoring_only", "Monitoring only"
    return {
        "level": level,
        "label": label,
        "controller": controller.name,
        "controller_description": controller.description,
        "thresholds_supported": thresholds_supported,
        "thresholds": ({"start": _threshold(start_path), "stop": _threshold(end_path)}
                       if thresholds_supported else None),
        "modes": modes,
        "active_mode": active,
        "mode_semantics": "Device-defined; Battery Guardian does not infer behavior from mode names.",
    }
