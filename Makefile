PYTHON := $(shell which python)
POETRY := poetry

all : test

test_install :
	$(POETRY) install

test: lint test_install
	$(POETRY) run pytest -ra -q

upload:
	$(POETRY) build && $(POETRY) publish -u __token__ -p $(PLOTDIGITIZER_TOKEN)

install:
	python3 -m pip install .

lint: mypy
	$(POETRY) run ruff check . 

mypy:
	$(POETRY) run mypy --ignore-missing-imports --install-types --non-interactive plotdigitizer tests

fmt:
	$(POETRY) run ruff format .

.PHONY: fmt mypy lint install upload test test_install all
