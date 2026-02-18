PYTHON := python3
CFLAGS := -shared -fPIC $(shell $(PYTHON)-config --includes)
LDFLAGS := $(shell $(PYTHON)-config --ldflags)

TARGET := src/slvrov_tools/pi2c_tools.so
SRC := src/slvrov_tools/clibs/pi2c_tools.c src/slvrov_tools/clibs/i2c_tools.c

all:
	gcc $(CFLAGS) $(SRC) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(TARGET)
