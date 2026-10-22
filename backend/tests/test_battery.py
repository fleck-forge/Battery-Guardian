from pathlib import Path

from battery_guardian.battery import read_snapshot


def make_power(root: Path, *, modes: str | None = None, start: str | None = None,
               stop: str | None = None, capacity: str = "73", status: str = "Discharging") -> Path:
    battery = root / "BATX"
    battery.mkdir(parents=True)
    (battery / "type").write_text("Battery\n")
    (battery / "present").write_text("1\n")
    (battery / "capacity").write_text(capacity + "\n")
    (battery / "status").write_text(status + "\n")
    if modes is not None:
        (battery / "charge_types").write_text(modes + "\n")
    if start is not None:
        (battery / "charge_control_start_threshold").write_text(start + "\n")
    if stop is not None:
        (battery / "charge_control_end_threshold").write_text(stop + "\n")
    adapter = root / "AC"
    adapter.mkdir()
    (adapter / "type").write_text("Mains\n")
    (adapter / "online").write_text("1\n")
    return battery


def test_snapshot_reads_battery_and_adapter(tmp_path: Path) -> None:
    make_power(tmp_path)
    snapshot = read_snapshot(tmp_path)
    assert snapshot.percentage == 73
    assert snapshot.status == "Discharging"
    assert snapshot.ac_connected is True
    assert snapshot.capability["label"] == "Monitoring only"


def test_preset_capability_and_active_name_are_reported_verbatim(tmp_path: Path) -> None:
    make_power(tmp_path, modes="Fast Standard [Long_Life]")
    capability = read_snapshot(tmp_path).capability
    assert capability["label"] == "Preset charging modes only"
    assert capability["modes"] == ["Fast", "Standard", "Long_Life"]
    assert capability["active_mode"] == "Long_Life"
    assert capability["thresholds"] is None


def test_thresholds_are_read_only_capability_data(tmp_path: Path) -> None:
    battery = make_power(tmp_path, start="50", stop="100")
    capability = read_snapshot(tmp_path).capability
    assert capability["thresholds_supported"] is True
    assert capability["thresholds"] == {"start": 50, "stop": 100}
    assert (battery / "charge_control_start_threshold").read_text() == "50\n"


def test_missing_battery_is_graceful(tmp_path: Path) -> None:
    snapshot = read_snapshot(tmp_path)
    assert snapshot.available is False
    assert snapshot.percentage is None
    assert snapshot.error
