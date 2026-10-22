"""Validated per-user configuration storage."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ThresholdConfig:
    start: int = 50
    stop: int = 100

    @classmethod
    def validate(cls, start: object, stop: object) -> "ThresholdConfig":
        # bool is an int subclass, but not a sensible threshold input.
        if type(start) is not int or type(stop) is not int:
            raise ValueError("Thresholds must be whole numbers from 0 through 100.")
        if not (0 <= start <= 100 and 0 <= stop <= 100):
            raise ValueError("Thresholds must be between 0 and 100.")
        if start >= stop:
            raise ValueError("The start threshold must be lower than the stop threshold.")
        return cls(start, stop)


def default_config_path() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "battery-guardian" / "config.json"


def load_config(path: Path | None = None) -> ThresholdConfig:
    config_path = path or default_config_path()
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        return ThresholdConfig.validate(data["start"], data["stop"])
    except FileNotFoundError:
        return ThresholdConfig()
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return ThresholdConfig()


def save_config(config: ThresholdConfig, path: Path | None = None) -> None:
    config_path = path or default_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = config_path.with_suffix(".json.tmp")
    temp_path.write_text(json.dumps({"start": config.start, "stop": config.stop}, indent=2) + "\n",
                         encoding="utf-8")
    temp_path.replace(config_path)
