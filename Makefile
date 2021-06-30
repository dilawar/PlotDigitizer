CMD = poetry run plotdigitizer

all : test4 test3 test2 test1

test_install :
	poetry install

test1: test_install
	$(CMD) figures/trimmed.png -p 0,0 -p 20,0 -p 0,1 \
	    -l 22,26 -l 142,23 -l 23,106 \
	    --plot ./figures/trimmed.result.png

test3 : test_install
	$(CMD) figures/graphs_1.png \
		-p 1,0 -p 6,0 -p 0,3 \
		-l 165,52 -l 599,51 -l 85,151 \
		--plot figures/graphs_1.result.png

test4 : test_install
	$(CMD) figures/ECGImage.png \
		-p 1,0 -p 5,0 -p 0,1 \
		-l 290,44 -l 1306,43 -l 106,301 \
		--plot figures/ECGImage.result.png \
		--debug

test5 : test_install
	$(CMD) figures/graph_with_grid.png \
		-p 100,0 -p 1000,0 -p 100,50 \
		-l 81,69 -l 1779,68 -l 81,449 \
		--plot figures/graph_with_grid.result.png


test: test1 test3 test4 test5
	poetry run pytest

upload:
	poetry build && poetry publish

install:
	python3 -m pip install .

lint:
	mypy
