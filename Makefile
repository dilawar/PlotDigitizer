PYTHON := $(shell which python)
POETRY := $(PYTHON) -m poetry

all : test

test_install :
	$(POETRY) install

test: lint test_install
	$(POETRY) run pytest -ra -q

upload:
	$(POETRY) build && $(POETRY) publish -u __token__ -p $(PLOTDIGITIZER_TOKEN)

install:
	python3 -m pip install .

lint:
	$(POETRY) run mypy --ignore-missing-imports --install-types --non-interactive plotdigitizer tests
