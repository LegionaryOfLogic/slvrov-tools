# Caleb Hofschneider SLVROV 2025

import smbus2 # type: ignore
from .misc_tools import fits_in_bits, at_exit


class I2C_Device:
    """
    A class for communicating with I2C devices using the smbus2 library.

    This class provides methods to read and write one or two bytes from/to registers on an I2C device.
    It handles bus management and ensures proper cleanup on exit or interruption.

    Attributes:
        address (int): I2C address of the device.
        bus_number (int): The I2C bus number (default is 1).
        bus (smbus2.SMBus): The underlying SMBus object for communication.
        closed (bool): Indicates whether the I2C connection is closed.
    """

    def __init__(self, address: int, bus: int=1):
        """
        Initializes an I2C_Device instance and opens a connection to the specified I2C bus.

        Args:
            address (int): The I2C address of the device.
            bus (int, optional): The I2C bus number to use (default is 1).
        """

        self.address = address
        self.bus_number = bus

        self.bus = smbus2.SMBus(bus)
        
        self.closed: bool = False
        at_exit(self.close)

    def write_byte(self, register: int, value: int):
        """
        Writes one byte to a given register.

        Args:
            register (int): A valid 8-bit register address on the I2C device.
            value (int): Numerical 8-bit value to write to the register.

        Raises:
            Exception: If register or value exceed 8-bit limits.
        """

        if not fits_in_bits(register, 8, False): raise Exception("Invalid register. Register value too big.")
        if not fits_in_bits(value, 8): raise Exception("Value is too big.")
        self.bus.write_byte_data(self.address, register, value)

    def read_byte(self, register: int) -> bytes:
        """
        Reads one byte from a given register on the I2C device.

        Args:
            register (int): The register number to read from.

        Returns:
            bytes: The byte (0-255) read from the register.

        Raises:
            Exception: If register exceeds 8-bit limits.
        """

        if not fits_in_bits(register, 8, False): raise Exception("Invalid register. Register value too big.")
        return self.bus.read_byte_data(self.address, register)

    def write_two_bytes(self, register: int, value: int):
        """
        Writes two bytes (a word) to a given register.

        Args:
            register (int): A valid 16-bit register address on the I2C device.
            value (int): Numerical 16-bit value to write to the register.

        Raises:
            Exception: If register or value exceed 16-bit limits.
        """

        if not fits_in_bits(register, 16, False): raise Exception("Invalid register. Register value too big.")
        if not fits_in_bits(value, 16): raise Exception("Value is too big.")
        self.bus.write_word_data(self.address, register, value)

    def read_two_bytes(self, register: int) -> bytes:
        """
        Reads two bytes (a word) from a given register on the I2C device.

        Args:
            register (int): The register number to read from.

        Returns:
            bytes: The 16-bit value (0-65535) read from the register.

        Raises:
            Exception: If register exceeds 8-bit limits.
        """

        if not fits_in_bits(register, 8, False): raise Exception("Invalid register. Register value too big.")
        return self.bus.read_word_data(self.address, register)
    
    def close(self):
        """
        Closes the I2C connection if it is not already closed.
        """

        if not self.closed: self.bus.close()

    def open(self, bus_number: int | None=None):
        """
        Reopens the I2C connection if it has been closed.

        Args:
            bus_number (int | None): Optional, default is None. If None, reuses the original bus number.
        """

        bus = self.bus_number if bus is None else bus_number

        if self.closed:
            self.bus.open(self.bus)