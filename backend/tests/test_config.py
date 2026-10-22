import pytest

from battery_guardian.config import ThresholdConfig, load_config, save_config


@pytest.mark.parametrize("start,stop", [(50, 100), (0, 1), (89, 90)])
def test_valid_thresholds(start: int, stop: int) -> None:
    assert ThresholdConfig.validate(start, stop) == ThresholdConfig(start, stop)


@pytest.mark.parametrize("start,stop", [(-1, 100), (50, 101), (100, 100), (70, 60), (True, 100), (50.0, 100)])
def test_invalid_thresholds(start: object, stop: object) -> None:
    with pytest.raises(ValueError):
        ThresholdConfig.validate(start, stop)


def test_config_round_trip(tmp_path) -> None:
    path = tmp_path / "nested" / "config.json"
    save_config(ThresholdConfig(55, 90), path)
    assert load_config(path) == ThresholdConfig(55, 90)
