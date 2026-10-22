"""Dependency-free fallback test runner: python3 backend/tests/run_tests.py"""

from __future__ import annotations

import tempfile
from pathlib import Path

from battery_guardian.battery import read_snapshot
from battery_guardian.config import ThresholdConfig, load_config, save_config
from battery_guardian.service import Backend


def fixture(root: Path, modes: str | None = None, thresholds: bool = False) -> Path:
    battery = root / "BAT0"
    battery.mkdir(parents=True)
    for name, value in {"type": "Battery", "present": "1", "capacity": "78", "status": "Discharging"}.items():
        (battery / name).write_text(value)
    if modes:
        (battery / "charge_types").write_text(modes)
    if thresholds:
        (battery / "charge_control_start_threshold").write_text("40")
        (battery / "charge_control_end_threshold").write_text("90")
    adapter = root / "AC"
    adapter.mkdir()
    (adapter / "type").write_text("Mains")
    (adapter / "online").write_text("1")
    return battery


def run() -> None:
    checks = 0
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        fixture(root, "Fast Standard [Long_Life]")
        state = read_snapshot(root)
        assert state.percentage == 78 and state.ac_connected is True
        assert state.capability["active_mode"] == "Long_Life"
        assert state.capability["label"] == "Preset charging modes only"
        checks += 1

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        battery = fixture(root, thresholds=True)
        start, stop = battery / "charge_control_start_threshold", battery / "charge_control_end_threshold"
        backend = Backend(root, root / "config.json")
        backend.set_preferences(50, 100)
        assert start.read_text() == "40" and stop.read_text() == "90"
        checks += 1

    for values in ((-1, 100), (50, 101), (100, 100), (80, 40), (True, 100)):
        try:
            ThresholdConfig.validate(*values)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted invalid thresholds: {values}")
        checks += 1

    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "prefs" / "config.json"
        save_config(ThresholdConfig(55, 90), path)
        assert load_config(path) == ThresholdConfig(55, 90)
        checks += 1

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        fixture(root)
        try:
            Backend(root, root / "config.json").set_preferences(50, 100)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted unsupported threshold preferences")
        checks += 1

    print(f"{checks} dependency-free checks passed")


if __name__ == "__main__":
    run()
