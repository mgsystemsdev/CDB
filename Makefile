PYTHON ?= python3
ROOT := $(shell pwd)

run:
	PYTHONPATH="$(ROOT)" $(PYTHON) -m src.main_cli --hours $(HOURS)

run-db:
	PYTHONPATH="$(ROOT)" $(PYTHON) -m src.main_cli --db $(DB) --item-id $(ITEM) --target-hours 5 --hours $(HOURS)

test:
	PYTHONPATH="$(ROOT)" pytest -q
