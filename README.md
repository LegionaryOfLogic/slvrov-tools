# slvrov-tools

A utility library for SLVROV that includes tools for:

- Non-trivial math operations
- Network communication
- Netowkr setup
- Exit handling
- Joysticks
- I2C control
- PCA9685 utils
- Misc tools
- CLI for gstreamer installation, udp video streaming

## Build From Source

0. Install dependencies

```bash
$ sudo apt install build-essential python3-dev
$ sudo apt install python3-opencv
```

1. Clone the repository

```bash
$ git clone https://github.com/LegionaryOfLogic/slvrov-tools
$ cd slvrov-tools
```
2. Compile C/Python shared library

```bash
/slvrov-tools$ make
```
3. Build Python library (if you wish to use it like a pip-installed package)

```bash
/slvrov-tools$ pip3 install .
```

