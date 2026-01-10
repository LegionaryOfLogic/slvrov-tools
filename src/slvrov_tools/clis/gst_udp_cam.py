#!/usr/bin/env python3
# Caleb Hofschneider SLVROV 12/2025

import argparse
from ..gst_tools import gst_install, gst_stream, gst_recieve
from ..misc_tools import sys_error

DEVICE="0"
FRAMERATE="30/1"
WXH = "1280x720"


def main() -> None:

    parser = argparse.ArgumentParser(description="A script to simplify the long and verbose gstreamer commands we use in ROV")

    parser.add_argument("-ip", help="IPV4 address to stream to")
    parser.add_argument("--port", "-p", type=int, help="Port to stream to or recieve from")
    parser.add_argument("--camera-index", "-c", default=DEVICE, type=int, help=f"Camera device index. Default is {DEVICE}")
    parser.add_argument("--dimensions", "-d", default=WXH, help=f"Video dimensions WidthxHeight. Default is {WXH}")
    parser.add_argument("--framerate", "-f", default=FRAMERATE, help=f"Camera framerate. Default is {FRAMERATE}")

    parser.add_argument("--stream", "-s", action="store_true", help="Flag to indicate stream action")
    parser.add_argument("--recieve", "-r", action="store_true", help="Flag to indicate recieve action")
    parser.add_argument("--install", "-i", action="store_true", help="Flag to indicate install action - MUST BE RUN TO STREAM OR RECIEVE. BREW IS REQUIRED ON MACOS")

    args = parser.parse_args()

    if args.stream:
        if args.recieve: sys_error("Cannot preform stream action and recieve action at the same time")
        if not args.ip or not args.port: sys_error("Both an IP address and port number are required for the stream action")

        gst_stream(args.ip, args.port, args.camera_index, args.dimensions, args.framerate)

    elif args.recieve:
        if args.stream: sys_error("Cannot preform recieve action and stream action at the same time")
        if not args.port: sys_error("Port number is required for recieving streams")

        gst_recieve(args.port)

    elif args.install: gst_install()
    else: sys_error("Action needed. Type '--help' or '-h' for usage")
    

if __name__ == "__main__":
    main()