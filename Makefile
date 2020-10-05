PY = python3
FIGURE = ./figures/trimmed.png

all : test
    

test: ./plotdigitizer.py
	$(PY) $< -i $(FIGURE) -p 0,0 -p 20,0 -p 0,1 \
	    -l 22,295 -l 142,296 -l 23,215 \
	    --plot

upload:
	twine upload 
