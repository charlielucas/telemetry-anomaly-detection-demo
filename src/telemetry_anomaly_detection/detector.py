"""Transparent baseline detector for telemetry rows."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median

from .simulate import SIGNALS


@dataclass(frozen=True)
class Baseline:
    medians: dict[str, float]
    scales: dict[str, float]


def median_absolute_deviation(values: list[float]) -> float:
    center = median(values)
    deviations = [abs(value - center) for value in values]
    return median(deviations) or 1.0


def fit_baseline(rows: list[dict[str, str]]) -> Baseline:
    medians: dict[str, float] = {}
    scales: dict[str, float] = {}

    for signal in SIGNALS:
        values = [float(row[signal]) for row in rows]
        medians[signal] = median(values)
        scales[signal] = median_absolute_deviation(values)

    return Baseline(medians=medians, scales=scales)


def score_row(row: dict[str, str], baseline: Baseline) -> dict[str, object]:
    signal_scores: dict[str, float] = {}

    for signal in SIGNALS:
        value = float(row[signal])
        scaled = abs(value - baseline.medians[signal]) / baseline.scales[signal]
        signal_scores[signal] = scaled

    top_signal = max(signal_scores, key=signal_scores.get)
    anomaly_score = signal_scores[top_signal]

    return {
        **row,
        "anomaly_score": f"{anomaly_score:.3f}",
        "top_signal": top_signal,
        "needs_review": str(anomaly_score >= 4.0),
    }


def score_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    baseline = fit_baseline(rows)
    return [score_row(row, baseline) for row in rows]
