PY = python3

all : test2 test1

test1: ./plotdigitizer.py
	$(PY) $< -i ./figures/trimmed.png -p 0,0 -p 20,0 -p 0,1 \
	    -l 22,295 -l 142,296 -l 23,215 \
	    --plot

test2: ./plotdigitizer.py
	$(PY) $< -i ./figures/un2.png -p 0,0 -p 20,0 -p 0,1 \
	    -l 2,754 -l 897,754 -l 643,583 \
	    --plot
upload:
	python3 setup.py bdist_wheel
	twine upload dist/*.whl

lint:
	mypy 
