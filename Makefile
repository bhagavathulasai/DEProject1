.PHONY: install test lint format check docker-up docker-down

PYTHON ?= python
PIP ?= $(PYTHON) -m pip

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt -r requirements-dev.txt

format:
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check . --fix

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check .

check: lint test

api:
	$(PYTHON) app.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v
