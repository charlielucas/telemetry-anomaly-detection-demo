"""Interactive review workspace for the synthetic telemetry detector."""

from __future__ import annotations

import csv
from io import StringIO

import streamlit as st

from telemetry_anomaly_detection.detector import (
    DEFAULT_REVIEW_THRESHOLD,
    baseline_for_row,
    fit_baselines,
    score_rows,
    signal_scores,
    summarize_detection,
)
from telemetry_anomaly_detection.simulate import SIGNALS, generate_rows

BASELINE_OPTIONS = {
    "Combined baseline": "combined",
    "Separate by operating mode": "mode",
}
SIGNAL_LABELS = {
    "bus_voltage": "Bus voltage",
    "battery_temp_c": "Battery temperature",
    "gyro_rate_dps": "Gyro rate",
    "reaction_wheel_rpm": "Reaction wheel speed",
    "downlink_snr_db": "Downlink signal-to-noise ratio",
}

st.set_page_config(
    page_title="Telemetry anomaly review",
    page_icon=None,
    layout="wide",
)


@st.cache_data
def telemetry_rows(seed: int) -> list[dict[str, object]]:
    return generate_rows(count=96, seed=seed)


def as_bool(value: object) -> bool:
    return value is True or str(value).lower() == "true"


def percent(value: float, denominator: int) -> str:
    return "n/a" if denominator == 0 else f"{value:.0%}"


def review_queue_csv(rows: list[dict[str, object]], include_labels: bool) -> str:
    fields = [
        "timestamp",
        "vehicle_id",
        "mode",
        "anomaly_score",
        "top_signal",
        "needs_review",
    ]
    if include_labels:
        fields.extend(["injected_event", "is_injected_anomaly"])
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


with st.sidebar:
    st.title("Review controls")
    baseline_label = st.radio(
        "Baseline",
        list(BASELINE_OPTIONS),
        key="baseline",
        help=(
            "The combined option fits one baseline to every row. The mode option fits "
            "separate baselines for sunlit and eclipse observations."
        ),
    )
    threshold = st.slider(
        "Review threshold",
        min_value=2.0,
        max_value=8.0,
        value=DEFAULT_REVIEW_THRESHOLD,
        step=0.1,
        key="threshold",
        help="A row enters the review queue when any signal reaches this robust z-score.",
    )
    seed = st.number_input(
        "Simulation seed",
        min_value=1,
        max_value=999,
        value=42,
        step=1,
        key="seed",
    )
    selected_signal_label = st.selectbox(
        "Timeline signal",
        list(SIGNAL_LABELS.values()),
        key="signal",
    )
    show_ground_truth = st.toggle(
        "Show injected event labels",
        value=True,
        key="ground_truth",
        help="These labels exist only because the data is synthetic.",
    )
    st.markdown(
        "[View the source on GitHub]"
        "(https://github.com/charlielucas/telemetry-anomaly-detection-demo)"
    )

baseline_scope = BASELINE_OPTIONS[baseline_label]
selected_signal = next(
    signal for signal, label in SIGNAL_LABELS.items() if label == selected_signal_label
)
rows = telemetry_rows(int(seed))
scored = score_rows(rows, threshold=threshold, baseline_scope=baseline_scope)
summary = summarize_detection(scored)
ranked = sorted(scored, key=lambda row: float(row["anomaly_score"]), reverse=True)
review_rows = [row for row in ranked if as_bool(row["needs_review"])]

st.title("Telemetry anomaly review")
st.write(
    "This app scores synthetic spacecraft telemetry, explains the signal behind each "
    "score, and routes high scoring rows into a review queue."
)
st.caption(
    "The injected event labels are available for evaluation because this is generated "
    "data. They would not be known during a real event."
)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Observations", summary["rows"])
m2.metric("Review queue", summary["review_count"])
m3.metric(
    "Events caught",
    f"{summary['true_positive']} / {summary['event_count']}",
)
m4.metric(
    "Precision",
    percent(float(summary["precision"]), int(summary["review_count"])),
)
m5.metric(
    "Recall",
    percent(float(summary["recall"]), int(summary["event_count"])),
)

if summary["false_negative"]:
    missed_count = int(summary["false_negative"])
    st.warning(
        f"{missed_count} injected {'event is' if missed_count == 1 else 'events are'} "
        "outside the review queue at the current threshold."
    )
elif summary["false_positive"]:
    extra_count = int(summary["false_positive"])
    st.info(
        f"All injected events are in the queue, along with {extra_count} unlabeled "
        f"{'row' if extra_count == 1 else 'rows'} that would also need review."
    )
else:
    st.success("All injected events are in the queue with no extra rows at this setting.")

st.header("Baseline comparison")
st.write(
    "The operating mode changes several normal signal ranges. Compare one combined "
    "baseline with separate sunlit and eclipse baselines before choosing a review policy."
)
comparison_rows = []
for label, scope in BASELINE_OPTIONS.items():
    comparison_summary = summarize_detection(
        score_rows(rows, threshold=threshold, baseline_scope=scope)
    )
    comparison_rows.append(
        {
            "baseline": label,
            "review rows": comparison_summary["review_count"],
            "events caught": (
                f"{comparison_summary['true_positive']} / "
                f"{comparison_summary['event_count']}"
            ),
            "false reviews": comparison_summary["false_positive"],
            "precision": percent(
                float(comparison_summary["precision"]),
                int(comparison_summary["review_count"]),
            ),
            "recall": percent(
                float(comparison_summary["recall"]),
                int(comparison_summary["event_count"]),
            ),
        }
    )
st.table(comparison_rows)

st.header("Signal timeline")
st.caption(
    f"{selected_signal_label}. Red points are rows in the review queue under the selected "
    "baseline and threshold."
)
timeline_rows = [
    {
        "timestamp": row["timestamp"],
        "value": float(row[selected_signal]),
        "needs_review": as_bool(row["needs_review"]),
        "mode": row["mode"],
        "score": float(row["anomaly_score"]),
        "top_signal": SIGNAL_LABELS[str(row["top_signal"])],
    }
    for row in scored
]
st.vega_lite_chart(
    timeline_rows,
    {
        "height": 320,
        "layer": [
            {
                "mark": {"type": "line", "color": "#4C78A8"},
                "encoding": {
                    "x": {"field": "timestamp", "type": "temporal", "title": "Time"},
                    "y": {
                        "field": "value",
                        "type": "quantitative",
                        "title": selected_signal_label,
                        "scale": {"zero": False},
                    },
                },
            },
            {
                "transform": [{"filter": "datum.needs_review == true"}],
                "mark": {"type": "point", "filled": True, "size": 80, "color": "#E45756"},
                "encoding": {
                    "x": {"field": "timestamp", "type": "temporal"},
                    "y": {"field": "value", "type": "quantitative"},
                    "tooltip": [
                        {"field": "timestamp", "type": "temporal", "title": "Time"},
                        {"field": "mode", "type": "nominal", "title": "Mode"},
                        {"field": "score", "type": "quantitative", "title": "Score"},
                        {
                            "field": "top_signal",
                            "type": "nominal",
                            "title": "Top signal",
                        },
                    ],
                },
            },
        ],
    },
    width="stretch",
)

st.header("Review queue")
if review_rows:
    display_rows = []
    for row in review_rows:
        display_row = {
            "timestamp": row["timestamp"],
            "mode": row["mode"],
            "score": row["anomaly_score"],
            "top signal": SIGNAL_LABELS[str(row["top_signal"])],
        }
        if show_ground_truth:
            display_row["injected event"] = row["injected_event"] or "none"
        display_rows.append(display_row)
    st.dataframe(display_rows, width="stretch", hide_index=True)
else:
    st.info("No rows meet the current review threshold.")

st.download_button(
    "Download review queue",
    data=review_queue_csv(review_rows, include_labels=show_ground_truth),
    file_name="telemetry_review_queue.csv",
    mime="text/csv",
)

st.subheader("Why this row was flagged")
review_candidates = review_rows or ranked[:8]
selected_timestamp = st.selectbox(
    "Review row",
    [str(row["timestamp"]) for row in review_candidates],
    key="review_row",
    format_func=lambda timestamp: next(
        (
            f"{timestamp} | {SIGNAL_LABELS[str(row['top_signal'])]} | "
            f"score {row['anomaly_score']}"
            for row in review_candidates
            if row["timestamp"] == timestamp
        ),
        timestamp,
    ),
)
selected_row = next(row for row in review_candidates if row["timestamp"] == selected_timestamp)
baselines = fit_baselines(rows, baseline_scope=baseline_scope)
selected_baseline = baseline_for_row(selected_row, baselines, baseline_scope)
selected_scores = signal_scores(selected_row, selected_baseline)
explanation_rows = [
    {
        "signal": SIGNAL_LABELS[signal],
        "observed": float(selected_row[signal]),
        "baseline median": round(selected_baseline.medians[signal], 3),
        "baseline MAD": round(selected_baseline.scales[signal], 3),
        "robust z-score": round(selected_scores[signal], 3),
    }
    for signal in SIGNALS
]
st.table(explanation_rows)
st.caption(
    "The row score is the largest signal score. The threshold determines whether that "
    "measurement enters the queue; it does not change the measurement itself."
)

with st.expander("What this demo does and does not show"):
    st.write(
        "The detector uses a transparent median and median absolute deviation baseline. "
        "It is useful for comparing review policies and explaining individual scores."
    )
    st.write(
        "It is not a production flight monitor. The data is synthetic, the injected events "
        "are simplified, and the detector does not use time windows, subsystem models, or "
        "operational alert rules."
    )
