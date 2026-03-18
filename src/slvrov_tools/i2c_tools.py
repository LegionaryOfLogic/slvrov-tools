from .misc_tools import fits_in_bits, at_exit
from .pi2c_tools import *


class I2C_Bus:
    """Wrapper around the low-level I2C bus bindings."""

    def __init__(self, bus: int, target_address: int | None = None):
        """Open an I2C bus and optionally set a default slave address.

        Args:
            bus (int): I2C bus number.
            target_address (int | None): Default slave address for read and write calls.
        """

        self.bus_number = bus
        self.bus = i2c_open_bus(f"/dev/i2c-{bus}")

        self.target_address = target_address

        at_exit(self.close)

    def write_byte_to(self, register: int, value: int, address: int | None = None):
        """Write a byte to a register on a target device.

        Args:
            register (int): Register address to write.
            value (int): Byte value to write.
            address (int | None): Override slave address.

        Raises:
            ValueError: If no target address is available.
            Exception: If the register or value is out of range.
        """

        if address is None: address = self.target_address
        if address is None: raise ValueError("No target address set and no address provided for write operation.")

        if not fits_in_bits(register, 8, False): raise Exception(f"Invalid register. Register value {register} too big.")
        if not fits_in_bits(value, 8): raise Exception(f"Value {value} is too big.")

        i2c_write_byte(self.bus, address, register, value)

    def read_byte_from(self, register: int, address: int | None = None) -> int:
        """Read a byte from a register on a target device.

        Args:
            register (int): Register address to read.
            address (int | None): Override slave address.

        Returns:
            int: Byte value read from the device.

        Raises:
            ValueError: If no target address is available.
            Exception: If the register is out of range.
        """

        if address is None: address = self.target_address
        if address is None: raise ValueError("No target address set and no address provided for read operation.")

        if not fits_in_bits(register, 8, False): raise Exception(f"Invalid register. Register value {register} too big.")

        return i2c_read_byte(self.bus, address, register)

    def close(self):
        """Close the open I2C bus handle if one exists."""

        if self.bus is not None:
            print("at_exit: Closing I2C bus...")
            i2c_close_bus(self.bus)
            self.bus = None

    def open(self, bus: int | None = None):
        """Open the I2C bus if it is currently closed.

        Args:
            bus (int | None): Optional new bus number to open.

        Raises:
            Exception: If the bus is already open.
        """

        if bus is not None: self.bus_number = bus
        if self.bus is not None: raise Exception("Bus is already open.")

        self.bus = i2c_open_bus(f"dev/i2c-{self.bus_number}")


class I2C_Slave:
    """Base helper for devices addressed on an ``I2C_Bus``."""

    def __init__(self, bus: I2C_Bus, address: int):
        """Store the bus and slave address for a device.

        Args:
            bus (I2C_Bus): I2C bus wrapper.
            address (int): Slave device address.
        """

        self.bus = bus
        self.address = address

    def write_byte(self, register: int, value: int):
        """Write a byte to one of this slave's registers.

        Args:
            register (int): Register address to write.
            value (int): Byte value to write.
        """

        if not fits_in_bits(register, 8, False): raise Exception(f"Invalid register. Register value {register} too big.")
        if not fits_in_bits(value, 8): Exception(f"Value {value} is too big.")

        self.bus.write_byte_to(register, value, self.address)

    def read_byte(self, register: int) -> int:
        """Read a byte from one of this slave's registers.

        Args:
            register (int): Register address to read.

        Returns:
            int: Value read from the device register.
        """

        if not fits_in_bits(register, 8, False): raise Exception(f"Invalid register. Register value {register} too big.")

        return self.bus.read_byte_from(register, self.address)
