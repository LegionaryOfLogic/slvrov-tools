from .misc_tools import fits_in_bits, at_exit
from .pi2c_tools import *


class I2C_Bus:
    def __init__(self, bus: int, target_address: int | None = None):
        self.bus_number = bus
        self.bus = i2c_open_bus(f"/dev/i2c-{bus}")

        self.target_address = target_address

        at_exit(self.close)

    def write_byte_to(self, register: int, value: int, address: int | None = None):
        if address is None: address = self.target_address
        if address is None: raise ValueError("No target address set and no address provided for write operation.")

        if not fits_in_bits(register, 8, False): raise Exception("Invalid register. Register value too big.")
        if not fits_in_bits(value, 8): raise Exception("Value is too big.")

        i2c_write_byte(self.bus, address, register, value)

    def read_byte_from(self, register: int, address: int | None = None) -> int:
        if address is None: address = self.target_address
        if address is None: raise ValueError("No target address set and no address provided for read operation.")

        if not fits_in_bits(register, 8, False): raise Exception("Invalid register. Register value too big.")

        return i2c_read_byte(self.bus, address, register)

    def close(self):
        if self.bus is not None:
            print("at_exit: Closing I2C bus...")
            i2c_close_bus(self.bus)
            self.bus = None

    def open(self, bus: int | None = None):
        if bus is not None: self.bus_number = bus
        if self.bus is not None: raise Exception("Bus is already open.")

        self.bus = i2c_open_bus(f"dev/i2c-{self.bus_number}")


class I2C_Slave:
    def __init__(self, bus: I2C_Bus, address: int):
        self.bus = bus
        self.address = address

    def write_byte(self, register: int, value: int):
        if not fits_in_bits(register, 8, False): raise Exception("Invalid register. Register value too big.")
        if not fits_in_bits(value, 8): raise Exception("Value is too big.")

        self.bus.write_byte_to(register, value, self.address)

    def read_byte(self, register: int) -> int:
        if not fits_in_bits(register, 8, False): raise Exception("Invalid register. Register value too big.")

        return self.bus.read_byte_from(register, self.address)