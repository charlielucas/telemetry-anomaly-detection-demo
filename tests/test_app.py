import unittest

from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def run_app(self) -> AppTest:
        app = AppTest.from_file("app.py", default_timeout=30).run()
        self.assertEqual(list(app.exception), [])
        return app

    @staticmethod
    def metrics(app: AppTest) -> dict[str, str]:
        return {metric.label: metric.value for metric in app.metric}

    def test_combined_baseline_shows_detection_tradeoff(self):
        app = self.run_app()

        self.assertEqual(self.metrics(app)["Events caught"], "3 / 4")
        self.assertEqual(self.metrics(app)["Recall"], "75%")

    def test_mode_baseline_catches_thermal_event(self):
        app = self.run_app()
        baseline_control = app.radio(key="baseline")
        app = baseline_control.set_value("Separate by operating mode").run()

        self.assertEqual(list(app.exception), [])
        self.assertEqual(self.metrics(app)["Events caught"], "4 / 4")
        self.assertEqual(self.metrics(app)["Recall"], "100%")

    def test_warning_reports_missed_and_extra_rows(self):
        app = self.run_app()
        app.number_input(key="seed").set_value(81)
        app.slider(key="threshold").set_value(2.0)
        app = app.run()

        self.assertEqual(list(app.exception), [])
        self.assertIn("1 injected event is outside", app.warning[0].value)
        self.assertIn("2 unlabeled rows", app.warning[0].value)


if __name__ == "__main__":
    unittest.main()
