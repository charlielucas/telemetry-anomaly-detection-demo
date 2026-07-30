import os
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
            scored = score(
                input_path=data_path,
                output_path=scored_path,
                baseline_scope="mode",
            )
            output = report(scored_path=scored_path, output_path=report_path)

            self.assertTrue(data_path.exists())
            self.assertTrue(scored_path.exists())
            self.assertTrue(report_path.exists())
            self.assertEqual(len(scored), 24)
            self.assertIn("Injected events flagged", output)

    def test_default_outputs_follow_current_working_directory(self):
        original_directory = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                os.chdir(tmpdir)
                generate(count=24)
                score()
                report()

                self.assertTrue(Path("data/telemetry.csv").exists())
                self.assertTrue(Path("examples/scored_telemetry.csv").exists())
                self.assertTrue(Path("examples/anomaly_report.md").exists())
            finally:
                os.chdir(original_directory)

    def test_report_rejects_negative_row_limit(self):
        with self.assertRaisesRegex(ValueError, "top_n must not be negative"):
            report(top_n=-1)


if __name__ == "__main__":
    unittest.main()
