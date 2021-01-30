CMD = poetry run plotdigitizer

all : test4 test3 test2 test1 

test_install : 
	poetry install

test1: test_install
	$(CMD) figures/trimmed.png -p 0,0 -p 20,0 -p 0,1 \
	    -l 22,295 -l 142,296 -l 23,215 \
	    --plot ./figures/trimmed.result.png

test2: test_install
	$(CMD) figures/un2.png -p 0,0 -p 20,0 -p 0,1 \
	    -l 2,754 -l 897,754 -l 643,583 \
	    --plot ./figures/un2.result.png 

test3 : test_install
	$(CMD) figures/graphs_1.png \
		-p 1,0 -p 6,0 -p 0,3 \
		-l 165,160 -l 599,160 -l 85,60 \
		--plot figures/graphs_1.result.png \
		--preprocess \
		--debug

test4 : test_install
	$(CMD) figures/ECGImage.png \
		-p 1,0 -p 5,0 -p 0,1 -l 290,337 \
		-l 1306,338 -l 106,83 \
		--plot figures/ECGImage.result.png \
		--debug

test: test_install
	poetry run pytest

upload:
	poetry build && poetry publish

install:
	python3 -m pip install .

lint:
	mypy 
