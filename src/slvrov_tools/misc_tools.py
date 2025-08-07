# Caleb Hofschneider SLVROV 2025

import atexit
import platform
import signal


def is_raspberry_pi() -> bool:
    """
    Discovers if the current device is a raspberry pi.

    Returns:
        bool: True if raspberry pi, False is not.
    """

    uname = platform.uname()
    return "raspberrypi" in uname.node.lower()


cleanup_functions_variable_that_no_one_will_ever_overwrite = []
def at_interrupt(func):
    """
    Adds function to a list to be exectuted at CTL-C.

    Args:
        func (function): The function to be run at CTL-C.
    """

    cleanup_functions_variable_that_no_one_will_ever_overwrite.append(func)


def interrupt_exec(signum, frame):
    """
    Runs at CTL-C and executes all of the functinos submitted by at_interrupt.
    """

    for func in cleanup_functions_variable_that_no_one_will_ever_overwrite:
        func()


def setup_interrupt_handlers():
    """
    Sets up the signal handers. Allows it so be called non-intrusively by the user.
    """

    global interrupt_exec
    signal.signal(signal.SIGINT, interrupt_exec)


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