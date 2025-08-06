# Caleb Hofschneider SLV ROV 1/2025

from dataclasses import dataclass


@dataclass
class PCA9685_Device_Descriptor:

    min_duty: int | None
    max_duty: int | None
    default: int
    pins: list
    action_header: str | None=None

    def __post_init__(self):
        if self.action_header is not None: self.encoded_action_header = self.action_header.value.encode()
        else: self.encoded_action_header = None

    def __repr__(self):
        return f"Duty Range: {self.min_duty}-{self.max_duty}, Default Duty: {self.default}, Pins: {self.pins}, Action Header: {self.action_header}, Encoded Header: {self.encoded_action_header}"
    def __str__(self):
        return f"Duty Range: {self.min_duty}-{self.max_duty}, Default Duty: {self.default}, Pins: {self.pins}"
    

from .misc_tools import is_raspberry_pi

if is_raspberry_pi():

    from i2c_device import I2C_Device
    from time import sleep

    class PCA9685(I2C_Device):
        """
        Class allowing basic use of the PCA9685 16-Channel, 12-bit PWM Driver.

        Attributes:
            pwm_frequency (int): The frequency (Hz) that the driver will output; max is 25_000_000.
            address (int): I2C address of the driver; default is 0x40.
            bus (int): I2C bus number; default is 1.
            pwm_time (int): The time (μs) it takes to complete one PWM cycle at pwm_frequency.

        Methods:
            clear(): Clears the MODE1 register, allowing the oscillator to start.
            write_prescale(): Calculates and writes the prescale that lowers the driver's clock frequency to the pwm frequency.
            write_duty_cycle(pin_number: int, pulse_length: float, start: int=0): Writes when the "on" pulse starts and stops; default start is 0.
        """

        def __init__(self, pwm_frequency: int, address: int=0x40, bus: int=1):
            """
            Initializes PCA9685_BASIC object attributes.

            Args:
                pwm_frequency (int): the frequency (Hz) that the driver will output; max is 25_000_000.
                address (int): I2C address of the driver; default is 0x40.
                bus (int): I2C bus number; default is 1.
            """

            super().__init__(address, bus)

            self.frequency = pwm_frequency


        def clear(self):
            """
            Clears the MODE1 register, turning off the SLEEP bit and allowing the oscillator to start.
            """

            self.write_byte(0x00, 0x00)  # Turns off SLEEP bit, allowing oscillator to start

        def write_prescale(self):
            """
            Calculates and writes the prescale that lowers the driver's clock frequency to the pwm frequency.
            """

            self.write_byte(0x00, 0x10)  # Allows PRE_SCALE to be written by setting the MODE1 register

            prescale = round(25_000_000 / (self.pwm_frequency * 4096) - 1)
            self.write_byte(0xFE, prescale)

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

            off_time = round(pulse_length / self.pwm_time * 4096)
            
            pin_offset = int(4 * pin_number)  # Python converts to float automatically, so need to convert back to int

            if not start: # Else duty starts at 0 seconds by default -- allows for future customization
                start *= 4096 / self.pwm_time
                
                self.write_byte(pin_offset + 6, start & 0xFF)
                self.write_byte(pin_offset + 7, start >> 8)

            self.write_byte(pin_offset + 8, off_time & 0xFF)  # Saves 8 low  bits
            self.write_byte(pin_offset + 9, off_time >> 8)  # Saves 4 high bits


    class Motor():
        """
        Class allowing the control over an ESC or servo through the PCA9685 PWM driver.

        Attributes:
            pin (int): the pin of the PCA8695 that the motor is on (0 - 15)
            min_duty (int): the length of the "on" pulse when the motor is at its minimum rotation (μs)
            max_duty (int): the length of the "on" pulse when the motor is at its maximum rotation (μs)
            max_rotation (int): the rotational range of the motor. This can be degrees for servos or 'levels' for motors (e.g. 100 fro 100% forward, 0 for 100% backwards)
            driver (PCA9685): PCA9685 driver being used to control the motor

        Methods:
            rotate(degrees): rotate motor to specified level of motion
        """

        def __init__(self, pin: int, min_duty: int, max_duty: int, max_rotation: int, pwm_frequency: int=50, address: int=0x40, bus: int=1):
            """
            Initializes Servo object with its attributes and sets up prescale

            Args:
                pin (int): the pin of the PCA8695 driver that the motor is on (0 - 15)
                min_duty (int): the length of the "on" pulse when the motor is at its minimum rotation (μs)
                max_duty (int): the length of the "on" pulse when the motor is at its maximum rotation (μs)
                max_rotation (int): the rotational range of the motor (degrees); default is 180˚
                pwm_frequency (int): the frequency (Hz) that the driver will output; max is 25_000_000
                address (int): I2C address of the PCA9685; default is 0x40
                bus (int): I2C bus number of the driver; default is 1
            """

            self.driver = PCA9685(pwm_frequency, address, bus)
            self.pin = pin

            self.min_duty = min_duty
            self.max_duty = max_duty

        def rotate(self, level: float, wait_time: int=0):
            """
            Rotate motor to a specified level of movement.

            Args:
                level (float): The amount of movement, ranging from 0 to the specified max_rotaiton. Fro motors, this would be the degree.
                wait_time (int): The time (in seconds) to wait in order to give the motor head to rotate if needed. Set to 0 by default.
            """

            pulse_length = level / self.max_rotation * (self.max_time - self.min_time) + self.min_time
            self.driver.write_duty_cycle(self.pin, pulse_length)

            sleep(wait_time)