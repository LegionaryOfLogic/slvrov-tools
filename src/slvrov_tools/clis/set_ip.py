#!/usr/bin/env python3
# Caleb Hofschneider SLVROV 12/2025

import argparse
from ipaddress import ip_address
from ..misc_tools import sys_error
from ..network_tools import has_NetworkManager, has_networkd, NetworkManager_modify_network, networkd_set_ip

RESERVED_START = "192.168.3.2"
RESERVED_END = "192.168.3.13"
BASE = "192.168.3"


def main() -> None:
    parser = argparse.ArgumentParser(description="Assign a static IPv4 address using nmcli with safety checks.")

    parser.add_argument("address", help="IPV4 address to assign to the interface")
    parser.add_argument("--connection", help=f"Name of network interface.")
    parser.add_argument("--override", action="store_true", help="Disable ROV address checks")

    args = parser.parse_args()

    try:
        addr = ip_address(args.address)
    except ValueError:
        sys_error(f"Invalid IP address: {args.address}")

    if ip_address(RESERVED_START) <= addr <= ip_address(RESERVED_END): sys_error(f"IP addresses {RESERVED_START} through {RESERVED_END} are reserved")
    if args.address == "192.168.3.0": sys_error(f"192.168.3.0 is special -- don't use it")
    if not args.address.startswith(BASE) and not args.override: sys_error(f"ROV is currently running on {BASE} IPs.")

    if has_NetworkManager(): NetworkManager_modify_network(args.address, args.connection)
    elif has_networkd(): networkd_set_ip(args.address, args.connection)
    else: sys_error("No supported network backend. Only work for NetworkManager or networkd")


if __name__ == "__main__":
    main()
