import unittest

from telemetry_anomaly_detection.detector import score_rows
from telemetry_anomaly_detection.simulate import generate_rows


class DetectorTests(unittest.TestCase):
    def test_detector_flags_injected_events(self):
        rows = generate_rows()
        scored = score_rows(rows)
        flagged = [row for row in scored if row["needs_review"] == "True"]

        self.assertGreaterEqual(len(flagged), 3)
        self.assertTrue(any(row["injected_event"] == "voltage sag" for row in flagged))

    def test_scored_rows_keep_context(self):
        row = score_rows(generate_rows(count=12))[0]

        self.assertIn("timestamp", row)
        self.assertIn("anomaly_score", row)
        self.assertIn("top_signal", row)


if __name__ == "__main__":
    unittest.main()
