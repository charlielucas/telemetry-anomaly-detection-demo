"""Generate deterministic synthetic telemetry."""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone


SIGNALS = [
    "bus_voltage",
    "battery_temp_c",
    "gyro_rate_dps",
    "reaction_wheel_rpm",
    "downlink_snr_db",
]


def generate_rows(count: int = 96, seed: int = 42) -> list[dict[str, object]]:
    rng = random.Random(seed)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    anomaly_points = {19, 47, 73, 88}
    rows: list[dict[str, object]] = []

    for index in range(count):
        orbit_phase = 2 * math.pi * (index % 24) / 24
        mode = "sunlit" if index % 24 < 15 else "eclipse"

        bus_voltage = 28.1 + 0.18 * math.sin(orbit_phase) + rng.uniform(-0.04, 0.04)
        battery_temp = 18.0 + 4.2 * math.sin(orbit_phase - 0.8) + rng.uniform(-0.35, 0.35)
        gyro_rate = 0.08 + rng.uniform(-0.025, 0.025)
        wheel_rpm = 3200 + 95 * math.sin(orbit_phase + 0.4) + rng.uniform(-22, 22)
        snr = 13.8 + 1.4 * math.cos(orbit_phase) + rng.uniform(-0.25, 0.25)

        injected_event = ""
        if index == 19:
            battery_temp += 8.0
            injected_event = "thermal rise"
        elif index == 47:
            gyro_rate += 0.31
            wheel_rpm += 420
            injected_event = "attitude control disturbance"
        elif index == 73:
            bus_voltage -= 1.2
            injected_event = "voltage sag"
        elif index == 88:
            snr -= 5.5
            injected_event = "downlink fade"

        rows.append(
            {
                "timestamp": (start + timedelta(minutes=10 * index)).isoformat(),
                "vehicle_id": "SAT-A",
                "mode": mode,
                "bus_voltage": round(bus_voltage, 3),
                "battery_temp_c": round(battery_temp, 3),
                "gyro_rate_dps": round(gyro_rate, 4),
                "reaction_wheel_rpm": round(wheel_rpm, 2),
                "downlink_snr_db": round(snr, 3),
                "injected_event": injected_event,
                "is_injected_anomaly": str(index in anomaly_points),
            }
        )

    return rows
