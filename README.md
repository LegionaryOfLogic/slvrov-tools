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

## CLI Usage

After `pip3 install .`, the package exposes a `set-ip` command for assigning
static `/24` IPv4 addresses on Ubuntu.

```bash
set-ip 192.168.3.20
set-ip 192.168.3.20 --interface eth0
set-ip 192.168.3.20 --interface eth0 --connection "Wired connection 1"
```

`set-ip` detects whether the machine is using NetworkManager or
`systemd-networkd` via netplan and applies the address using the appropriate
backend.

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
