import tempfile
import unittest
from pathlib import Path

from telemetry_anomaly_detection.cli import generate, report, score


class CliTests(unittest.TestCase):
    def test_workflow_writes_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            data_path = tmp_path / "telemetry.csv"
            scored_path = tmp_path / "scored.csv"
            report_path = tmp_path / "report.md"

            generate(output_path=data_path, count=24)
            score(input_path=data_path, output_path=scored_path)
            output = report(scored_path=scored_path, output_path=report_path)

            self.assertTrue(data_path.exists())
            self.assertTrue(scored_path.exists())
            self.assertTrue(report_path.exists())
            self.assertIn("Injected events flagged", output)


if __name__ == "__main__":
    unittest.main()
