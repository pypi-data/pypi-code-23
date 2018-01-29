"""Makefile template"""

MAKEFILE_TEMPLATE = """CC = gcc
CFLAGS = -Wall -std=c99
OUTFILE = bin/{name}
OBJ = ./obj/{name}.o
SRC = ./src/{name}.c


$(OUTFILE): $(OBJ)
	$(CC) -o $(OUTFILE) $(OBJ) $(CFLAGS)
$(OBJ): $(SRC)
	$(CC) -o $(OBJ) -c $(SRC) $(CFLAGS)

clean:
	$(RM) ./obj/* ./bin/*
"""
