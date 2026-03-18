# slvrov-tools

`slvrov-tools` is a Python utility package for SLVROV development. The repo currently provides helpers for math and geometry, Linux joystick input, OpenCV camera capture, UDP networking, static IP configuration, GStreamer camera streaming, and I2C/PCA9685 device control.

## Current capabilities

- `slvrov_tools.math_tools`: numeric helpers, point rotation, circle mapping/clamping, and a bounded integer wrapper.
- `slvrov_tools.misc_tools`: platform detection, exit hooks, subprocess helpers, and bit-width checks.
- `slvrov_tools.cv2_tools`: OpenCV camera open/warm-up helpers and image capture utilities.
- `slvrov_tools.joystick_tools`: blocking and asyncio-based Linux joystick readers plus callback-driven execution helpers.
- `slvrov_tools.network_tools`: generic socket communicators, UDP send/receive helpers, and Linux network configuration helpers for NetworkManager or `systemd-networkd`.
- `slvrov_tools.i2c_tools`: wrappers around the repo's low-level I2C bindings.
- `slvrov_tools.pca9685`: JSON-backed pin configuration helpers and an I2C PCA9685 driver wrapper.
- `slvrov_tools.legacy_pca9685`: older `smbus2`-based PCA9685 and servo helpers retained for compatibility.
- CLI entry points:
  - `set-ip`: assign a static IPv4 address using the supported Linux network backend.
  - `udp-cam`: install GStreamer, stream camera video over UDP, or receive a UDP video stream.

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
