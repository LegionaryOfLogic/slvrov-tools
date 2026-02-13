# Caleb Hofschneider SLVROV 12/2024

import struct
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from .misc_tools import at_exit


class JoystickEventType(Enum):
    button = 1
    axis = 2
    button_on_startup = 129
    axis_on_startup = 130


@dataclass
class JoystickEvent:
    time: int
    event_type: JoystickEventType
    type_index: int
    value: int


def get_available_joysticks(path_to_joysticks: str="/dev/input/", joystick_fd_prefix="js") -> list[int]:
    joystick_indices = [int(file.name[2:]) for file in Path(path_to_joysticks).glob(f"{joystick_fd_prefix}*")]
    return joystick_indices


class SimpleJoystick:
    def __init__(self, index: int, packet_size: int=8, data_format: str="IhBB"):
        self.device = open(f"/dev/input/js{index}", "rb")
        self.packet_size = packet_size
        self.data_format = data_format

        at_exit(self.device.close)

    def get_event(self) -> JoystickEvent:

        input_data = self.device.read(self.packet_size)
        time, value, event_type, type_index = struct.unpack(self.data_format, input_data)

        return JoystickEvent(time, JoystickEventType(event_type), type_index, value)


class ExecutorJoystick(SimpleJoystick):
    def __init__(self, index: int, axis_funcs: list, button_funcs: list, packet_size: int= 8, data_format: str= "IhBB"):
        super().__init__(index, packet_size, data_format)

        self.axis_funcs = axis_funcs
        self.button_funcs = button_funcs

        self.axis = [0 for _ in axis_funcs]
        self.buttons = [0 for _ in button_funcs]

    def interpret_event(self, event: JoystickEvent):
        
        if event.event_type == JoystickEventType.axis: self.axis[event.type_index] = -event.value
        elif event.event_type == JoystickEventType.button: self.buttons[event.type_index] = event.value
        else: raise NotImplementedError(f"{event.event_type} has not been implemented in this function yet.\nCurrently supports button and axis events")

    def execute_events(self):
        
        for axis_value, axis_func in zip(self.axis, self.axis_funcs): axis_func(axis_value)
        for button_value, button_func in zip(self.buttons, self.button_funcs): button_func(button_value)