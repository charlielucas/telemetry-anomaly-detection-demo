PYTHON ?= python3

.PHONY: test demo generate score report

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests

generate:
	PYTHONPATH=src $(PYTHON) -m telemetry_anomaly_detection generate

score:
	PYTHONPATH=src $(PYTHON) -m telemetry_anomaly_detection score

report:
	PYTHONPATH=src $(PYTHON) -m telemetry_anomaly_detection report

demo: generate score report
