CMD = poetry run plotdigitizer

all : test

test_install :
	poetry install

test: test_install
	poetry run pytest -ra -q

upload:
	poetry build && poetry publish -u __token__ -p $(PYPI_TOKEN)

install:
	python3 -m pip install .

lint:
	mypy
