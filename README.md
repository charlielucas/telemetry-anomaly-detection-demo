# Telemetry Anomaly Review

A small Python and Streamlit project for finding and reviewing unusual points in
synthetic spacecraft telemetry.

The data is generated for this repo. It is not flight data, employer data, or
data from a real mission.

## What It Does

The workflow generates a telemetry table, scores each row against a transparent
baseline, and routes high scoring observations into a review queue.

The example focuses on a few signals that are easy to reason about:

- bus voltage
- battery temperature
- gyro rate
- reaction wheel speed
- downlink signal-to-noise ratio

The detector uses robust z-scores based on median and median absolute deviation.
The app shows the observed value, baseline, score, and review decision for each
signal so the result stays inspectable.

The review controls make two policy choices visible:

- Use one combined baseline or separate baselines for sunlit and eclipse modes.
- Adjust the score threshold that sends a row to review.

For the default synthetic dataset, the combined baseline catches three of four
injected events. Separate mode baselines catch all four. That comparison is part
of the demo because a useful detector needs a baseline that reflects the system's
normal operating states.

## Interactive App

Use Python 3.10 or newer. Create an environment and install the project:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Then launch the review workspace:

```bash
streamlit run app.py
```

The app includes:

- baseline and threshold controls
- a side-by-side policy comparison
- a signal timeline with review markers
- precision and recall against known synthetic labels
- a downloadable review queue
- row-level score explanations

## Project Structure

```text
telemetry-anomaly-detection-demo/
  app.py
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
    test_app.py
    test_cli.py
    test_detector.py
    test_simulate.py
  Makefile
  requirements.txt
```

## Command Line Workflow

Use Python 3.10 or newer.

```bash
telemetry-anomaly generate
telemetry-anomaly score
telemetry-anomaly report
```

The score command also accepts the same policy choices shown in the app:

```bash
telemetry-anomaly score --baseline-scope mode --threshold 3.5
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

This is not a production detector. It is a compact example of the kind of workflow
I like: make data checks visible, keep the score understandable, and give a
reviewer enough context to decide what needs attention.

The review queue is the output. A score does not automate an operational decision.

## Known Limits

- The telemetry is synthetic.
- The detector treats rows independently.
- The injected events are simplified and are not a complete failure model.
- There are no time-window features or subsystem-specific operating rules.
- The default evaluation uses the same generated sequence that fits the baseline.
