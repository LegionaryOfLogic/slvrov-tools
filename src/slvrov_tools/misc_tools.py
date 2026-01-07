# Caleb Hofschneider SLVROV 2025

import atexit
import platform
import subprocess
import sys


def is_raspberry_pi() -> bool:
    """
    Discovers if the current device is a raspberry pi.

    Returns:
        bool: True if raspberry pi, False is not.
    """

    uname = platform.uname()
    return "raspberrypi" in uname.node.lower()

def sys_error(msg: str, exit_code: int=1) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(exit_code)


def get_os():
    os = platform.system()
    if os in ["Darwin", "Linux"]: return os
    else: raise Exception(f"{os} is not supported") 


def at_exit(func):
    """
    Allows a function to be run when the program terminates smoothly.

    Args:
        func (function): The function to be exectued.
    """

    atexit.register(func)


def fits_in_bits(i: int, bits: int, signed: bool | None=None) -> bool:
    """
    Determines if a given int i fits into a given amount of bits.

    Args:
        i (int): The integer in question.
        bits (int): The given amount of bits.
        signed (bool | None): Is the int signed. Default is None, in which case both are tested.

    Returns:
        bool: True if i can be represented by the given number of bits, False if not.
    """

    signed_range = (- (2 ** (bits / 2) - 1), 2 ** (bits / 2))
    unsigned_range = (0, 2 ** bits - 1)

    if signed is None: return signed_range[0] <= i <= signed_range[1] or unsigned_range[0] <= i <= unsigned_range[1]
    elif signed: mn, mx = signed_range
    else: mn, mx = unsigned_range

    return mn <= i <= mx


def safe_run(command: list[str], error_msg: str | None=None, exit_at_exception: bool=False, exit_code: int=1, print_error: bool=True) -> None:

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        msg = error_msg if error_msg is not None else ''
        if print_error: msg += f"\n{error}"

        if exit_at_exception: sys_error(msg, exit_code)
        else: print(msg)



import locale


def install_jazzy_ros() -> None:
    """
    Function for installing jazzy ros2. See details at https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html.
    If any part of this process fails, consider manually following the steps given on the website.
    """

    current_locale: tuple[str | None, str | None] = locale.getlocale()

    # Setting the locale to en_US.UTF-8
    if '.'.join(current_locale) != "en_US.UTF-8": 
        print("Setting locale LANG to en_US.UTF-8...")

        update_and_install_locales: list[str] = ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "locales"]
        locale_gen: list[str] = ["sudo", "locale-gen", "en_US", "en_US.UTF-8"]
        update_locale: list[str] = ["sudo", "update-locale", "LC_ALL=en_US.UTF-8", "LANG=en_US.UTF-8"]
        export: list[str] = ["export", "LANG=en_US.UTF-8"]

        safe_run(update_and_install_locales, "Problem updating and installing locales")
        safe_run(locale_gen, "Problem with locale-gen command")
        safe_run(update_locale, "Problem updating locale")
        safe_run(export, "Problem exporting locale")

    install_software_properties_common: list[str] = ["sudo", "apt", "install", "software-properties-common"]
    add_universe_repo: list[str] = ["sudo", "add-apt-repository universe"]

    safe_run(install_software_properties_common, "Problem installing software-properties-common")
    safe_run(add_universe_repo, "Problem adding universe repo")

    curl_install: list[str] = ["sudo", "apt", "install", "curl", "-y"]
    export_ros_apt_src_vers: list[str] = ["export", "ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest", "|", "grep", "-F", "tag_name", "|", "awk", "-F\" '{print $4}')"]
    curl_deb_stuff: list[str] = ["curl", "-L", "-o", "/tmp/ros2-apt-source.deb", "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"]
    dpkg: list[str] = ["sudo", "dpkg", "-i", "/tmp/ros2-apt-source.deb"]
    dev_tools: list[str] = ["sudo", "apt", "install", "ros-dev-tools"]
    update: list[str] = ["sudo", "apt", "update"]

    safe_run(curl_install, "Problem installing curl")
    safe_run(export_ros_apt_src_vers, "Problem exporting ROS_APT_SOURCE_VERSION")
    safe_run(curl_deb_stuff, "Problem curling debian github stuff")
    safe_run(dpkg, "Problem with dpkg stuff")
    safe_run(dev_tools, "Problemn installing ros2 dev tools")
    safe_run(update, "Problem with sudo apt update")