import unittest

from telemetry_anomaly_detection.simulate import generate_rows


class SimulateTests(unittest.TestCase):
    def test_generation_is_deterministic(self):
        first = generate_rows(count=10, seed=7)
        second = generate_rows(count=10, seed=7)

        self.assertEqual(first, second)
        self.assertEqual(len(first), 10)

    def test_generation_includes_injected_events(self):
        rows = generate_rows()
        events = [row for row in rows if row["is_injected_anomaly"] == "True"]

        self.assertEqual(len(events), 4)


if __name__ == "__main__":
    unittest.main()
