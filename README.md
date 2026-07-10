# Telemetry Anomaly Detection

A small Python project for finding unusual points in synthetic spacecraft telemetry.

The data is generated for this repo. It is not flight data, employer data, or data from a real mission.

## What It Does

The workflow generates a simple telemetry table, scores each row against a baseline, and writes a report of the highest risk points.

The example focuses on a few signals that are easy to reason about:

- bus voltage
- battery temperature
- gyro rate
- reaction wheel speed
- downlink signal-to-noise ratio

The detector is intentionally transparent. It uses robust z-scores based on median and median absolute deviation. That makes the output easy to inspect and explain.

## Project Structure

```text
telemetry-anomaly-detection-demo/
  data/
    telemetry.csv
  examples/
    anomaly_report.md
    scored_telemetry.csv
  src/
    telemetry_anomaly_detection/
      __main__.py
      cli.py
      detector.py
      io.py
      simulate.py
  tests/
    test_detector.py
    test_simulate.py
  Makefile
```

## Quick Start

Use Python 3.9 or newer.

```bash
PYTHONPATH=src python3 -m telemetry_anomaly_detection generate
PYTHONPATH=src python3 -m telemetry_anomaly_detection score
PYTHONPATH=src python3 -m telemetry_anomaly_detection report
```

Or use the Makefile:

```bash
make test
make demo
```

## Outputs

The commands write:

- `data/telemetry.csv`
- `examples/scored_telemetry.csv`
- `examples/anomaly_report.md`

The report lists the top scored rows and the signal that contributed most to each score.

## Design Notes

This is not meant to be a production detector. It is a compact example of the kind of workflow I like: make the data checks visible, keep the score understandable, and give a reviewer enough context to decide what needs attention.

A larger version would add mode-specific baselines, time-window features, calibration against labeled events, and operational thresholds by subsystem.

## Known Limits

- The telemetry is synthetic.
- The baseline is global rather than mode-specific.
- The detector treats rows independently.
- The report is small and text-based by design.

## Safety Notes

- no real mission data
- no employer data
- no internal schema names
- no credentials or API keys
- no private work code
