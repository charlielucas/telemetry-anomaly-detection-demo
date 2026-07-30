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
        baseline_control = next(
            radio for radio in app.radio if radio.key == "baseline"
        )
        app = baseline_control.set_value("Separate by operating mode").run()

        self.assertEqual(list(app.exception), [])
        self.assertEqual(self.metrics(app)["Events caught"], "4 / 4")
        self.assertEqual(self.metrics(app)["Recall"], "100%")


if __name__ == "__main__":
    unittest.main()
