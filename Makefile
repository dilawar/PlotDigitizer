PYTHON := $(shell which python)
POETRY := $(PYTHON) -m poetry

all : test

test_install :
	$(POETRY) install

test: test_install
	$(POETRY) run pytest -ra -q

upload:
	$(POETRY) build && $(POETRY) publish -u __token__ -p $(PYPI_TOKEN)

install:
	python3 -m pip install .

lint:
	mypy
