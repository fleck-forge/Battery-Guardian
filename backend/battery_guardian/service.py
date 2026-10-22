"""Session D-Bus monitoring service (no privileged methods)."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
from pathlib import Path
from typing import Any

from .battery import read_snapshot
from .config import ThresholdConfig, default_config_path, load_config, save_config

BUS_NAME = "org.batteryguardian.Service"
OBJECT_PATH = "/org/batteryguardian/Service"
INTERFACE = "org.batteryguardian.Service"
LOG = logging.getLogger("battery_guardian")


class Backend:
    def __init__(self, root: Path = Path("/sys/class/power_supply"), config_path: Path | None = None):
        self.root = root
        self.config_path = config_path or default_config_path()
        self.config = load_config(self.config_path)

    def get_state(self) -> dict[str, Any]:
        state = read_snapshot(self.root).to_dict()
        state["configuration"] = {"start": self.config.start, "stop": self.config.stop}
        if not state["capability"]["thresholds_supported"]:
            state["configuration_note"] = "Saved preferences are not applied: this device has no adjustable threshold interface."
        return state

    def set_preferences(self, start: int, stop: int) -> dict[str, Any]:
        capability = read_snapshot(self.root).to_dict()["capability"]
        if not capability["thresholds_supported"]:
            raise ValueError("Adjustable thresholds are not supported by the detected battery interface.")
        config = ThresholdConfig.validate(start, stop)
        self.config = config
        save_config(config, self.config_path)
        # Deliberately does not write sysfs: this release only stores preferences.
        return self.get_state()


async def serve() -> None:
    try:
        from dbus_next.aio import MessageBus
        from dbus_next.service import ServiceInterface, method
    except ImportError as exc:
        raise RuntimeError("Install the 'dbus' optional dependency to run the service") from exc

    backend = Backend()

    class GuardianInterface(ServiceInterface):
        def __init__(self) -> None:
            super().__init__(INTERFACE)

        @method()
        def GetState(self) -> "s":
            return json.dumps(backend.get_state(), separators=(",", ":"))

    bus = await MessageBus().connect()
    bus.export(OBJECT_PATH, GuardianInterface())
    await bus.request_name(BUS_NAME)
    LOG.info("D-Bus service ready on %s", BUS_NAME)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            pass
    await stop.wait()
    bus.disconnect()


def main() -> None:
    logging.basicConfig(level=os.environ.get("BATTERY_GUARDIAN_LOG_LEVEL", "INFO"),
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")
    try:
        asyncio.run(serve())
    except Exception:
        LOG.exception("Service stopped")
        raise


if __name__ == "__main__":
    main()
