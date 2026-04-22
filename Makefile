PYTHON ?= python

.PHONY: help run-mock garak normalize score plots all

help:
	@echo "make run-mock    - start the local mock target"
	@echo "make garak       - run detector baseline"
	@echo "make normalize   - normalize outputs into one CSV"
	@echo "make score       - compute metrics"
	@echo "make plots       - render charts"
	@echo "make all         - garak + normalize + score + plots"

run-mock:
	uvicorn frameworks.common.mock_target:app --host 0.0.0.0 --port 8000

garak:
	$(PYTHON) frameworks/garak/run_garak.py

normalize:
	$(PYTHON) scripts/normalize_results.py

score:
	$(PYTHON) scripts/score_metrics.py

plots:
	$(PYTHON) scripts/plot_results.py

all: garak normalize score plots
