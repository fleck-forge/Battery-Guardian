import pytest

from battery_guardian.service import Backend


def fixture_battery(root, thresholds=False):
    battery = root / "BAT0"
    battery.mkdir(parents=True)
    for name, value in {"type": "Battery", "present": "1", "capacity": "80", "status": "Charging"}.items():
        (battery / name).write_text(value)
    if thresholds:
        (battery / "charge_control_start_threshold").write_text("40")
        (battery / "charge_control_end_threshold").write_text("90")
    return battery


def test_rejects_setting_thresholds_without_hardware(tmp_path):
    fixture_battery(tmp_path)
    backend = Backend(tmp_path, tmp_path / "config.json")
    with pytest.raises(ValueError, match="not supported"):
        backend.set_preferences(50, 100)
    assert not (tmp_path / "config.json").exists()


def test_threshold_preferences_are_stored_without_sysfs_writes(tmp_path):
    battery = fixture_battery(tmp_path, thresholds=True)
    start = battery / "charge_control_start_threshold"
    stop = battery / "charge_control_end_threshold"
    backend = Backend(tmp_path, tmp_path / "config.json")
    backend.set_preferences(50, 100)
    assert start.read_text() == "40"
    assert stop.read_text() == "90"


def test_preferences_validate_order(tmp_path):
    fixture_battery(tmp_path, thresholds=True)
    backend = Backend(tmp_path, tmp_path / "config.json")
    with pytest.raises(ValueError, match="lower"):
        backend.set_preferences(100, 50)
