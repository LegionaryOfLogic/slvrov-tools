#!/usr/bin/env python3
# Caleb Hofschneider SLVROV 12/2025

import argparse
from ipaddress import ip_address
from .misc_tools import sys_error
from .network_tools import cycle_connection, nmcli_modify

RESERVED_START = "192.168.3.2"
RESERVED_END = "192.168.3.13"
GATEWAY = "192.168.3.1"
DNS = "8.8.8.8"
CONNECTION_NAME = "Wired Connection 1"
BASE = "192.168.3"


def main() -> None:
    parser = argparse.ArgumentParser(description="Assign a static IPv4 address using nmcli with safety checks.")

    parser.add_argument("address", help="IPV4 address to assign to the interface")
    parser.add_argument("--gateway", default=GATEWAY, help=f"IPV4 gateway address. Default is {GATEWAY}")
    parser.add_argument("--connection", default=CONNECTION_NAME, help=f"Name of network interface. Default is {CONNECTION_NAME}")
    parser.add_argument("--no-cycle", action="store_true", help="Do not bring the connection down and up after applying changes")
    parser.add_argument("--dns", default=DNS, help=f"IPV4 DNS address. Default is {DNS}")
    parser.add_argument("--override", action="store_true", help="Disable ROV address checks")

    args = parser.parse_args()

    try:
        addr = ip_address(args.address)
    except ValueError:
        sys_error(f"Invalid IP address: {args.address}")

    if ip_address(RESERVED_START) <= addr <= ip_address(RESERVED_END): sys_error(f"IP addresses {RESERVED_START} through {RESERVED_END} are reserved")
    if args.address == "192.168.3.0": sys_error(f"192.168.3.0 is special -- don't use it")
    if not args.address.startswith(BASE) and not args.override: sys_error(f"ROV is currently running on {BASE} IPs. Use '--override 1' for non-ROV uses")

    nmcli_modify(args.address, args.gateway, args.connection, args.dns)
    if not args.no_cycle: cycle_connection(args.connection)


if __name__ == "__main__":
    main()
