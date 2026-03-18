#!/usr/bin/env python3
# Caleb Hofschneider SLVROV 12/2025

import argparse
from ipaddress import ip_address
from ..misc_tools import sys_error
from ..network_tools import pick_default_interface, set_static_ipv4

RESERVED_START = "192.168.3.2"
RESERVED_END = "192.168.3.13"
BASE = "192.168.3"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assign a static /24 IPv4 address on Ubuntu using NetworkManager or systemd-networkd."
    )

    parser.add_argument("address", help="IPV4 address to assign to the interface")
    parser.add_argument(
        "--interface",
        default=None,
        help="Linux interface name to configure. Defaults to eth0 when present, otherwise the first non-loopback interface.",
    )
    parser.add_argument(
        "--connection",
        default=None,
        help="NetworkManager connection profile to modify. Usually not needed because it can be derived from --interface.",
    )
    parser.add_argument("--override", action="store_true", help="Disable ROV address checks")

    args = parser.parse_args()

    try:
        addr = ip_address(args.address)
    except ValueError:
        sys_error(f"Invalid IP address: {args.address}")

    if addr.version != 4:
        sys_error(f"IPv6 is not supported by set-ip: {args.address}")

    if not args.override and ip_address(RESERVED_START) <= addr <= ip_address(RESERVED_END): sys_error(f"IP addresses {RESERVED_START} through {RESERVED_END} are reserved")
    if args.address == "192.168.3.0": sys_error(f"192.168.3.0 is special -- don't use it")
    if not args.address.startswith(BASE) and not args.override: sys_error(f"ROV is currently running on {BASE} IPs.")

    resolved_interface = args.interface
    try:
        if resolved_interface is None:
            resolved_interface = pick_default_interface()

        backend, target = set_static_ipv4(
            ipv4_address=args.address,
            interface_name=resolved_interface,
            connection_name=args.connection,
        )
    except Exception as error:
        sys_error(str(error))

    print(
        f"Set {resolved_interface} to {args.address}/24 using {backend} "
        f"({target})."
    )


if __name__ == "__main__":
    main()
