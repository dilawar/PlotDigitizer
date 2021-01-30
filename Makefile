PY = python3

all : test4 test3 test2 test1 

test1: ./plotdigitizer.py
	$(PY) $< ./figures/trimmed.png -p 0,0 -p 20,0 -p 0,1 \
	    -l 22,295 -l 142,296 -l 23,215 \
	    --plot ./figures/trimmed.result.png

test2: ./plotdigitizer.py
	$(PY) $< ./figures/un2.png -p 0,0 -p 20,0 -p 0,1 \
	    -l 2,754 -l 897,754 -l 643,583 \
	    --plot ./figures/un2.result.png 

test3 : ./plotdigitizer.py
	$(PY) ./plotdigitizer.py figures/graphs_1.png \
		-p 1,0 -p 6,0 -p 0,3 \
		-l 165,160 -l 599,160 -l 85,60 \
		--plot figures/graphs_1.result.png \
		--preprocess \
		--debug

test4 : ./plotdigitizer.py
	$(PY) ./plotdigitizer.py figures/ECGImage.png \
		-p 1,0 -p 5,0 -p 0,1 -l 290,337 \
		-l 1306,338 -l 106,83 \
		--plot figures/ECGImage.result.png \
		--debug


upload:
	python3 setup.py bdist_wheel
	twine upload dist/*.whl

lint:
	mypy 
