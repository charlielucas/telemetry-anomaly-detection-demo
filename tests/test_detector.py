import unittest

from telemetry_anomaly_detection.detector import (
    DEFAULT_REVIEW_THRESHOLD,
    score_rows,
    summarize_detection,
)
from telemetry_anomaly_detection.simulate import SIGNALS, generate_rows


class DetectorTests(unittest.TestCase):
    def test_detector_flags_injected_events(self):
        rows = generate_rows()
        scored = score_rows(rows)
        flagged = [row for row in scored if row["needs_review"] == "True"]

        self.assertEqual(len(flagged), 3)
        self.assertEqual(summarize_detection(scored)["recall"], 0.75)

    def test_mode_baselines_catch_all_injected_events(self):
        scored = score_rows(generate_rows(), baseline_scope="mode")
        summary = summarize_detection(scored)

        self.assertEqual(summary["true_positive"], 4)
        self.assertEqual(summary["false_positive"], 0)
        self.assertEqual(summary["recall"], 1.0)

    def test_scored_rows_keep_context(self):
        row = score_rows(generate_rows(count=12))[0]

        self.assertIn("timestamp", row)
        self.assertIn("anomaly_score", row)
        self.assertIn("top_signal", row)

    def test_threshold_changes_policy_without_changing_score(self):
        rows = generate_rows()
        default = score_rows(rows, threshold=DEFAULT_REVIEW_THRESHOLD)
        strict = score_rows(rows, threshold=8.0)

        self.assertEqual(
            [row["anomaly_score"] for row in default],
            [row["anomaly_score"] for row in strict],
        )
        self.assertGreater(
            summarize_detection(default)["review_count"],
            summarize_detection(strict)["review_count"],
        )

    def test_rejects_invalid_policy_settings(self):
        for threshold in (0, -1, float("nan"), float("inf")):
            with self.subTest(threshold=threshold):
                with self.assertRaisesRegex(ValueError, "review threshold"):
                    score_rows(generate_rows(), threshold=threshold)

        with self.assertRaisesRegex(ValueError, "unknown baseline scope"):
            score_rows(generate_rows(), baseline_scope="vehicle")

    def test_rejects_non_finite_signal_values(self):
        for value in ("nan", "inf", "not-a-number"):
            with self.subTest(value=value):
                rows = generate_rows(count=12)
                rows[0]["bus_voltage"] = value

                with self.assertRaisesRegex(ValueError, "bus_voltage must be a finite"):
                    score_rows(rows)

    def test_zero_mad_flags_departure_from_constant_signal(self):
        rows = generate_rows(count=5)
        for row in rows:
            for signal in SIGNALS:
                row[signal] = 1.0
        rows[-1]["bus_voltage"] = 1.1

        scored = score_rows(rows)

        self.assertEqual(scored[-1]["anomaly_score"], "inf")
        self.assertEqual(scored[-1]["needs_review"], "True")

    def test_empty_input_returns_empty_scores(self):
        self.assertEqual(score_rows([]), [])


if __name__ == "__main__":
    unittest.main()
