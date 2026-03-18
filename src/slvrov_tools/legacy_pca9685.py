# Caleb Hofschneider SLV ROV 1/2025

import smbus2  # type: ignore -- smbus should be included on Raspberry Pis
from time import sleep


class PCA9685_BASIC:
    """
    Class allowing basic use of the PCA9685 16-Channel, 12-bit PWM Driver

    Attributes:
        pwm_frequency (int): the frequency (Hz) that the driver will output; max is 25_000_000
        address (int): I2C address of the driver; default is 0x40
        bus (int): I2C bus number; default is 1
        pwm_time (int): the time (μs) it takes to complete one PWM cycle at pwm_frequency

    Methods:
        write(register, value): writes a value to a given register on the PCA9685
        clear(): clears the MODE1 register, allowing the oscillator to start
        write_prescale(): calculates and writes the prescale that lowers the driver's clock frequency to the pwm frequency
        write_duty_cycle(pin_number, pulse_length, start): writes when the "on" pulse starts and stops; default start is 0
    """

    def __init__(self, pwm_frequency, address=0x40, bus=1):
        """
        Initializes PCA9685_BASIC object attributes.

        Args:
            pwm_frequency (int): Output PWM frequency in hertz.
            address (int): I2C address of the driver.
            bus (int): I2C bus number.
        """
        self.bus = smbus2.SMBus(bus)
        self.address = address
        self.pwm_frequency = pwm_frequency
        self.pwm_time = 1_000_000 / pwm_frequency

        self.write_prescale()

    def write(self, register, value):
        """
        Writes a value to a given register on the PCA9685

        Args:
            register (int): Valid PCA9685 register address.
            value (int): Whole-number value to write.
        """
        self.bus.write_byte_data(self.address, register, value)

    def clear(self):
        """
        Clear the MODE1 register so the oscillator can start.
        """
        self.write(0x00, 0x00)  # Turns off SLEEP bit, allowing oscillator to start

    def write_prescale(self):
        """
        Calculate and write the prescale for the configured PWM frequency.
        """
        self.write(0x00, 0x10)  # Allows PRE_SCALE to be written
        prescale = round(25_000_000 / (self.pwm_frequency * 4096) - 1)
        self.write(0xFE, prescale)
        self.clear()  # Starts oscillator

    def write_duty_cycle(self, pin_number, pulse_length, start=0):
        """
        Writes when the "on" pulse starts and stops; default start is 0

        Args:
            pin_number (int): Output pin number from 0 to 15.
            pulse_length (float): Length of the on pulse in microseconds.
            start (int): Pulse start offset in microseconds.
        """
        if pin_number > 15:
            raise Exception("Pin number out of range")

        off_time = round(pulse_length / self.pwm_time * 4096)
        pin_offset = int(4 * pin_number)  # Python converts to float automatically, so need to convert back to int

        if start != 0:  # Else duty starts at 0 seconds by default -- allows for future customization
            start *= 4096 / self.pwm_time
            self.write(pin_offset + 6, start & 0xFF)
            self.write(pin_offset + 7, start >> 8)

        self.write(pin_offset + 8, off_time & 0xFF)  # Saves 8 low bits
        self.write(pin_offset + 9, off_time >> 8)  # Saves 4 high bits


class Servo:
    """
    Class allowing the control over a servo compatible with the PCA9685 driver

    Attributes:
        pin (int): the pin of the PCA8695 that the servo is on (0 - 15)
        min_time (float): the length of the "on" pulse when the servo is at its minimum rotation (μs)
        max_time (float): the length of the "on" pulse when the servo is at its maximum rotation (μs)
        max_rotation (int): the rotational range of the servo (degrees); default is 180˚
        driver (Legacy_PCA9685_BASIC): PCA9685 driver being used to control the servo

    Methods:
        rotate(degrees): rotate servo to specified degrees
        stop(): terminates duty cycle to stop servo rotating - can be moved again using rotate
    """

    def __init__(self, pin, min_time, max_time, max_rotation=180, pwm_frequency=50, address=0x40, bus=1):
        """
        Initializes Servo object with its attributes and sets up prescale

        Args:
            pin (int): PCA9685 output pin from 0 to 15.
            min_time (float): Pulse length at minimum rotation in microseconds.
            max_time (float): Pulse length at maximum rotation in microseconds.
            max_rotation (int): Maximum supported servo rotation in degrees.
            pwm_frequency (int): Driver PWM frequency in hertz.
            address (int): I2C address of the PCA9685.
            bus (int): I2C bus number.
        """
        self.pin = pin
        self.min_time = min_time
        self.max_time = max_time
        self.max_rotation = max_rotation

        self.driver = PCA9685_BASIC(pwm_frequency, address, bus)
        self.driver.write_prescale()

    def rotate(self, degrees, wait_time):
        """
        Rotate the servo to a specified angle.

        Args:
            degrees (float): Desired servo angle in degrees.
            wait_time (float): Time in seconds to wait for movement to complete.
        """
        pulse_length = degrees / self.max_rotation * (self.max_time - self.min_time) + self.min_time
        self.driver.write_duty_cycle(self.pin, pulse_length)
        sleep(wait_time)  # Allows enough time for the servo head to move (if needed)

    def stop(self):
        """
        Stop driving the servo by writing a zero-length pulse.
        """
        self.driver.write_duty_cycle(self.pin, 0)
