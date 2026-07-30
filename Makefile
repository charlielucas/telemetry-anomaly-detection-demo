PYTHON ?= python3
RUFF ?= ruff

.PHONY: check lint test demo generate score report app

check: lint test

lint:
	$(RUFF) check .
	$(RUFF) format --check .

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests

generate:
	PYTHONPATH=src $(PYTHON) -m telemetry_anomaly_detection generate

score:
	PYTHONPATH=src $(PYTHON) -m telemetry_anomaly_detection score

report:
	PYTHONPATH=src $(PYTHON) -m telemetry_anomaly_detection report

demo: generate score report

app:
	streamlit run app.py
