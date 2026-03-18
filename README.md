# slvrov-tools

`slvrov-tools` is a Python utility package for SLVROV development. The repo currently provides helpers for math and geometry, Linux joystick input, OpenCV camera capture, UDP networking, static IP configuration, GStreamer camera streaming, and I2C/PCA9685 device control.

## Current capabilities

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

## Installation

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
<<<<<<< HEAD

The package declares `opencv-python` as a dependency. Some modules also rely on system-level tools or hardware-specific components:

```bash
$ sudo apt install build-essential python3-dev
$ sudo apt install python3-opencv
```

- Linux joystick support expects `/dev/input/js*` devices.
- GStreamer commands require `gst-launch-1.0` and related plugins.
- Network configuration helpers call `nmcli`, `systemctl`, `netplan`, and `sudo`.
- I2C helpers depend on the bundled low-level bindings and access to `/dev/i2c-*`.
- `legacy_pca9685` requires `smbus2`.

## CLI usage

Start a UDP camera stream:

```bash
udp-cam --stream -ip 192.168.3.20 --port 5000
```

Receive a UDP camera stream:

```bash
udp-cam --recieve --port 5000
```

Set a static IP address:

```bash
set-ip 192.168.3.20 --connection eth0
```
=======
>>>>>>> codex/networkd_ip_script
