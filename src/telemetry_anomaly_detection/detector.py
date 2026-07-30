"""Transparent baseline detector for telemetry rows."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median

from .simulate import SIGNALS

DEFAULT_REVIEW_THRESHOLD = 3.5
ROBUST_Z_SCALE = 0.6744897501960817
BASELINE_SCOPES = {"combined", "mode"}


@dataclass(frozen=True)
class Baseline:
    medians: dict[str, float]
    scales: dict[str, float]


def median_absolute_deviation(values: list[float]) -> float:
    center = median(values)
    deviations = [abs(value - center) for value in values]
    return median(deviations) or 1.0


def fit_baseline(rows: list[dict[str, object]]) -> Baseline:
    if not rows:
        raise ValueError("cannot fit a baseline without telemetry rows")

    medians: dict[str, float] = {}
    scales: dict[str, float] = {}

    for signal in SIGNALS:
        values = [float(row[signal]) for row in rows]
        medians[signal] = median(values)
        scales[signal] = median_absolute_deviation(values)

    return Baseline(medians=medians, scales=scales)


def fit_baselines(
    rows: list[dict[str, object]], baseline_scope: str = "combined"
) -> dict[str, Baseline]:
    """Fit one baseline for all rows or one baseline per operating mode."""
    if baseline_scope not in BASELINE_SCOPES:
        raise ValueError(f"unknown baseline scope: {baseline_scope}")
    if not rows:
        return {}
    if baseline_scope == "combined":
        return {"combined": fit_baseline(rows)}

    modes = sorted({str(row["mode"]) for row in rows})
    return {
        mode: fit_baseline([row for row in rows if str(row["mode"]) == mode])
        for mode in modes
    }


def baseline_for_row(
    row: dict[str, object],
    baselines: dict[str, Baseline],
    baseline_scope: str,
) -> Baseline:
    key = "combined" if baseline_scope == "combined" else str(row["mode"])
    return baselines[key]


def signal_scores(row: dict[str, object], baseline: Baseline) -> dict[str, float]:
    """Return absolute robust z-scores for each telemetry signal."""
    scores: dict[str, float] = {}

    for signal in SIGNALS:
        value = float(row[signal])
        scaled = (
            ROBUST_Z_SCALE
            * abs(value - baseline.medians[signal])
            / baseline.scales[signal]
        )
        scores[signal] = scaled

    return scores


def score_row(
    row: dict[str, object],
    baseline: Baseline,
    threshold: float = DEFAULT_REVIEW_THRESHOLD,
) -> dict[str, object]:
    scores = signal_scores(row, baseline)
    top_signal = max(scores, key=scores.get)
    anomaly_score = scores[top_signal]

    return {
        **row,
        "anomaly_score": f"{anomaly_score:.3f}",
        "top_signal": top_signal,
        "needs_review": str(anomaly_score >= threshold),
    }


def score_rows(
    rows: list[dict[str, object]],
    threshold: float = DEFAULT_REVIEW_THRESHOLD,
    baseline_scope: str = "combined",
) -> list[dict[str, object]]:
    if threshold <= 0:
        raise ValueError("review threshold must be positive")
    baselines = fit_baselines(rows, baseline_scope=baseline_scope)
    return [
        score_row(
            row,
            baseline_for_row(row, baselines, baseline_scope),
            threshold=threshold,
        )
        for row in rows
    ]


def summarize_detection(rows: list[dict[str, object]]) -> dict[str, object]:
    """Compare the review policy with the known labels in the synthetic data."""

    def true_value(value: object) -> bool:
        return value is True or str(value).lower() == "true"

    true_positive = sum(
        true_value(row["needs_review"]) and true_value(row["is_injected_anomaly"])
        for row in rows
    )
    false_positive = sum(
        true_value(row["needs_review"]) and not true_value(row["is_injected_anomaly"])
        for row in rows
    )
    false_negative = sum(
        not true_value(row["needs_review"]) and true_value(row["is_injected_anomaly"])
        for row in rows
    )
    true_negative = len(rows) - true_positive - false_positive - false_negative
    review_count = true_positive + false_positive
    event_count = true_positive + false_negative

    return {
        "rows": len(rows),
        "review_count": review_count,
        "event_count": event_count,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "true_negative": true_negative,
        "precision": true_positive / review_count if review_count else 0.0,
        "recall": true_positive / event_count if event_count else 0.0,
    }
