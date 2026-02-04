# Caleb Hofschneider SLVROV 2025

import smbus2 # type: ignore
from .misc_tools import fits_in_bits, at_exit


import smbus2  # type: ignore
from .misc_tools import fits_in_bits, at_exit


class I2C_Bus:
    """
    Convenience wrapper around smbus2.SMBus for basic I2C register access.

    This class provides simple helper methods for reading and writing
    8-bit and 16-bit values to I2C device registers, with optional
    per-call address overrides.

    The bus is automatically closed on program exit via `at_exit`.
    """

    def __init__(self, target_address: int | None = None, bus: int = 1):
        """
        Initialize the I2C bus.

        Parameters
        ----------
        target_address : int | None, optional
            Default I2C device address to use for read/write operations.
            If None, an address must be provided explicitly per call.
        bus : int, default=1
            I2C bus number (e.g. 1 for /dev/i2c-1).
        """
        self.target_address = target_address
        self.bus_number = bus

        self.bus = smbus2.SMBus(bus)
        self.closed: bool = False

        # Ensure the bus is closed when the program exits
        at_exit(self.close)

    def write_byte(self, register: int, value: int, address: int | None = None):
        """
        Write a single byte to an 8-bit register.

        Parameters
        ----------
        register : int
            Register address (must fit in 8 bits).
        value : int
            Value to write (must fit in 8 bits).
        address : int | None, optional
            I2C device address to use for this operation.
            If None, `self.target_address` is used.

        Raises
        ------
        Exception
            If the register or value does not fit within the allowed bit width.
        """
        if not fits_in_bits(register, 8, False):
            raise Exception("Invalid register. Register value too big.")
        if not fits_in_bits(value, 8):
            raise Exception("Value is too big.")

        self.bus.write_byte_data(
            self.target_address if address is None else address,
            register,
            value,
        )

    def read_byte(self, register: int, address: int | None = None) -> bytes:
        """
        Read a single byte from an 8-bit register.

        Parameters
        ----------
        register : int
            Register address (must fit in 8 bits).
        address : int | None, optional
            I2C device address to use for this operation.
            If None, `self.target_address` is used.

        Returns
        -------
        bytes
            The byte read from the register.

        Raises
        ------
        Exception
            If the register does not fit within the allowed bit width.
        """
        if not fits_in_bits(register, 8, False):
            raise Exception("Invalid register. Register value too big.")

        return self.bus.read_byte_data(
            self.target_address if address is None else address,
            register,
        )

    def write_two_bytes(self, register: int, value: int, address: int | None = None):
        """
        Write a 16-bit value to a register.

        Parameters
        ----------
        register : int
            Register address (must fit in 16 bits).
        value : int
            Value to write (must fit in 16 bits).
        address : int | None, optional
            I2C device address to use for this operation.
            If None, `self.target_address` is used.

        Raises
        ------
        Exception
            If the register or value does not fit within the allowed bit width.
        """
        if not fits_in_bits(register, 16, False):
            raise Exception("Invalid register. Register value too big.")
        if not fits_in_bits(value, 16):
            raise Exception("Value is too big.")

        self.bus.write_word_data(
            self.target_address if address is None else address,
            register,
            value,
        )

    def read_two_bytes(self, register: int, address: int | None = None) -> bytes:
        """
        Read a 16-bit value from a register.

        Parameters
        ----------
        register : int
            Register address (must fit in 8 bits).
        address : int | None, optional
            I2C device address to use for this operation.
            If None, `self.target_address` is used.

        Returns
        -------
        bytes
            The 16-bit value read from the register.

        Raises
        ------
        Exception
            If the register does not fit within the allowed bit width.
        """
        if not fits_in_bits(register, 8, False):
            raise Exception("Invalid register. Register value too big.")

        return self.bus.read_word_data(self.address, register)

    def close(self):
        """
        Close the underlying I2C bus.

        This method is idempotent and is automatically called at program exit.
        """
        if not self.closed:
            self.bus.close()

    def open(self, bus_number: int | None = None):
        """
        Open the I2C bus if it has been closed.

        Parameters
        ----------
        bus_number : int | None, optional
            Bus number to open. If None, the originally configured bus number
            is used.
        """
        bus = self.bus_number if bus is None else bus_number

        if self.closed:
            self.bus.open(self.bus)