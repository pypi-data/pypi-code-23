"""Makefile template"""

MAKEFILE_TEMPLATE = """CC = gcc
CFLAGS = -Wall -std=c99
OUTFILE = {path}/bin/{name}
OBJ = {path}/obj/{name}.o
SRC = {path}/src/{name}.c


$(OUTFILE): $(OBJ)
	$(CC) -o $(OUTFILE) $(OBJ) $(CFLAGS)
$(OBJ): $(SRC)
	$(CC) -o $(OBJ) -c $(SRC) $(CFLAGS)

clean:
	$(RM) {path}/obj/* {path}/bin/*
"""
