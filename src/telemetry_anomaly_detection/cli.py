"""Command line entry points for the telemetry workflow."""

from __future__ import annotations

import argparse
from pathlib import Path

from .detector import score_rows
from .io import read_csv, write_csv
from .simulate import SIGNALS, generate_rows


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "telemetry.csv"
SCORED_PATH = ROOT / "examples" / "scored_telemetry.csv"
REPORT_PATH = ROOT / "examples" / "anomaly_report.md"


def generate(output_path: Path = DATA_PATH, count: int = 96, seed: int = 42) -> list[dict[str, object]]:
    rows = generate_rows(count=count, seed=seed)
    fieldnames = [
        "timestamp",
        "vehicle_id",
        "mode",
        *SIGNALS,
        "injected_event",
        "is_injected_anomaly",
    ]
    write_csv(output_path, rows, fieldnames)
    return rows


def score(input_path: Path = DATA_PATH, output_path: Path = SCORED_PATH) -> list[dict[str, object]]:
    rows = read_csv(input_path)
    scored = score_rows(rows)
    fieldnames = list(scored[0].keys()) if scored else []
    write_csv(output_path, scored, fieldnames)
    return scored


def report(scored_path: Path = SCORED_PATH, output_path: Path = REPORT_PATH, top_n: int = 8) -> str:
    rows = read_csv(scored_path)
    ranked = sorted(rows, key=lambda row: float(row["anomaly_score"]), reverse=True)
    review_rows = [row for row in rows if row["needs_review"] == "True"]
    injected_rows = [row for row in rows if row["is_injected_anomaly"] == "True"]
    flagged_injected_rows = [row for row in injected_rows if row["needs_review"] == "True"]

    lines = [
        "# Anomaly Report",
        "",
        f"- Scored rows: {len(rows)}",
        f"- Rows needing review: {len(review_rows)}",
        f"- Injected events: {len(injected_rows)}",
        f"- Injected events flagged: {len(flagged_injected_rows)}",
        "",
        "## Highest Scored Rows",
        "",
        "| timestamp | mode | score | top signal | injected event |",
        "| --- | --- | ---: | --- | --- |",
    ]

    for row in ranked[:top_n]:
        lines.append(
            "| {timestamp} | {mode} | {anomaly_score} | {top_signal} | {injected_event} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "Scores use robust distance from the median. The report is meant to",
            "surface rows for review, not to automate an operational decision.",
            "",
        ]
    )

    output = "\n".join(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic telemetry anomaly workflow")
    parser.add_argument("command", choices=["generate", "score", "report"])
    parser.add_argument("--data-path", type=Path, default=DATA_PATH)
    parser.add_argument("--scored-path", type=Path, default=SCORED_PATH)
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    parser.add_argument("--count", type=int, default=96)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--top-n", type=int, default=8)
    args = parser.parse_args()

    if args.command == "generate":
        rows = generate(output_path=args.data_path, count=args.count, seed=args.seed)
        print(f"Wrote {len(rows)} telemetry rows to {args.data_path}")
    elif args.command == "score":
        rows = score(input_path=args.data_path, output_path=args.scored_path)
        print(f"Wrote {len(rows)} scored rows to {args.scored_path}")
    elif args.command == "report":
        print(report(scored_path=args.scored_path, output_path=args.report_path, top_n=args.top_n))


if __name__ == "__main__":
    main()
