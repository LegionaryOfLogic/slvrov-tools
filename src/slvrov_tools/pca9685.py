# Caleb Hofschneider SLV ROV 1/2025

from dataclasses import dataclass
from time import sleep
from .i2c_bus import I2C_Bus


@dataclass
class PCA9685_Pin_Config:
    name: str
    pins: list[int]
    minimum: int
    default: int
    maximum: int

    def _prep_json(self):
        return self.name, {"pins": self.pins, "minimum": self.minimum, "default": self.default, "maximum": self.maximum}
    

from json import load, dump

def write_pca9685_pin_configs(configs: list[PCA9685_Pin_Config], json_file: str, indent=2) -> None:
    json_dict = {}

    for config in configs:
        name, config_json = config._prep_json()

        if name in json_dict: raise NameError(f"Name {name} already exists in pwm pin configs. Each config must have a unique str as a name.")
        json_dict[name] = config_json

    with open(json_file, "w") as file:
        dump(json_dict, file, indent=indent)


def append_pca9685_pin_configs(configs: list[PCA9685_Pin_Config], json_file: str, indent=2) -> None:
    with open(json_file, 'r') as file:
        configs_json: dict = load(file)

        for config in configs:
            name, config_json = config._prep_json()

            if name in configs_json: raise NameError(f"Name {name} already exists in pwm pin configs. Each config must have a unique str as a name.")
            configs_json[name] = config_json

        dump(configs_json, file, indent=indent)


def get_pin_configs(pwm_config_file: str) -> dict:
    with open(pwm_config_file, "r") as file:
        configs = load(file)
    
    return configs
    

class PCA9685():

    def __init__(self, pwm_frequency: int, bus: I2C_Bus, address: int=0x40):

        self.bus = bus
        self.address = address
        
        self.write_byte = self.bus.write_byte
        self.read_byte = self.bus.read_byte
        self.write_two_bytes = self.bus.write_two_bytes
        self.read_two_bytes = self.bus.read_two_bytes

        self.pwm_frequency = pwm_frequency
        self.pwm_time = 1_000_000 / pwm_frequency

    def clear(self):
        """
        Clears the MODE1 register, turning off the SLEEP bit and allowing the oscillator to start.
        """

        self.write_byte(0x00, 0x00, self.address)  # Turns off SLEEP bit, allowing oscillator to start

    def write_prescale(self):
        """
        Calculates and writes the prescale that lowers the driver's clock frequency to the pwm frequency.
        """

        self.write_byte(0x00, 0x10, self.address)  # Allows PRE_SCALE to be written by setting the MODE1 register
        prescale = round(25_000_000 / (self.pwm_frequency * 4096) - 1)
        self.write_byte(0xFE, prescale, self.address)
        self.clear()  # Starts oscillator

    def write_duty_cycle(self, pin_number: int, pulse_length: float, start: int=0):
        """
        Writes when the "on" pulse starts and stops; default start is 0

        Args:
            pin_number (int): the desired pin number of the ouput on the PCA9685 driver, numbers 0 - 15
            pulse_length (float): the length of the "on" part of the PWM cycle (μs)
            start (int): how long into the PWM cycle to start the "on" signal (μs); default is 0

        Raises:
            Exception: If pin number is out of range.
        """

        if pin_number > 15: raise Exception("Pin number out of range")

        # The naming 'off time' is confusing. The cycle will be on for the duration of off_time, so the time it will turn off will be the value of off_time
        off_time = round(pulse_length / self.pwm_time * 4096)
        pin_offset = int(4 * pin_number)  # Python converts to float automatically, so need to convert back to int

        if start:  # Else duty starts at 0 seconds by default -- allows for future customization
            start *= 4096 / self.pwm_time
            self.write_byte(pin_offset + 6, start & 0xFF, self.address)
            self.write_byte(pin_offset + 7, start >> 8)

        self.write_byte(pin_offset + 8, off_time & 0xFF, self.address)  # Saves 8 low bits
        self.write_byte(pin_offset + 9, off_time >> 8, self.address)  # Saves 4 high bits