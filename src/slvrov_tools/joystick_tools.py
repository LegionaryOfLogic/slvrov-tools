# Caleb Hofschneider SLVROV 12/2024

import struct
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from .misc_tools import at_exit


class JoystickEventType(Enum):
    # Caleb Hofschneider SLVROV 02/2026

    button = 1
    axis = 2
    button_on_startup = 129
    axis_on_startup = 130


@dataclass
class JoystickEvent:
    # Caleb Hofschneider SLVROV 02/2026

    time: int
    event_type: JoystickEventType
    type_index: int
    value: int


def get_available_joysticks(path_to_joysticks: str="/dev/input/", joystick_fd_prefix="js") -> list[int]:
    # Caleb Hofschneider SLVROV 02/2026

    joystick_indices = [int(file.name[2:]) for file in Path(path_to_joysticks).glob(f"{joystick_fd_prefix}*")]
    return joystick_indices


class SimpleJoystick:
    # Caleb Hofschneider SLVROV 02/2026, taken from 12/2024 joystick code
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
    # Caleb Hofschneider SLVROV 12/2024, updated/refactored 02/2026

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


import asyncio
import os

class AsyncJoystick:
    def __init__(self, index: int, callback=None, packet_size: int=8, data_format: str="IhBB"):
        self.index = index
        self.callback = callback
        self.started = False

        self.packet_size = packet_size
        self.data_format = data_format

        self.path = f"/dev/input/js{self.index}"
        self.fd = None

        self.latest_event = None
        self.waiting = []

    def start(self):
        if self.started: return

        self.fd = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)
        self.started = True

        loop = asyncio.get_running_loop()
        loop.add_reader(self.fd, self.on_joystick_ready)

    def stop(self):
        if not self.started: return

        loop = asyncio.get_running_loop()
        loop.remove_reader(self.fd)

        os.close(self.fd)

        self.fd = None
        self.started = False

    def on_joystick_ready(self):
        try:
            js_input = os.read(self.fd, self.packet_size)

            # if we recieve an incomplete or empty bytestring from os.read()
            if len(js_input) < self.packet_size or not js_input: return

            time, value, event_type, type_index = struct.unpack(self.data_format, js_input)
            self.latest_event = JoystickEvent(time, value, event_type, type_index)

            # clears waiting list to prevent race condition (I think? it was something AI said to fix)
            waiting = self.waiting
            self.waiting = []

            # fufils get_eventc calls waiting for js input
            for empty_future in waiting:
                if not empty_future.done(): empty_future.set_result(self.latest_event)
            self.waiting.clear()

            if self.callback is not None: self.callback(self.latest_event)

        except BlockingIOError:
            return

    async def get_event(self) -> JoystickEvent:
        if self.latest_event is not None: 

            # prevents race condition (thanks ChatGPT)
            # if used in a while loop, this will keep returning the same event until the joystick moves
            event = self.latest_event
            self.latest_event = None  # therefore we must set the latest event to none

            return event

        # adds this call of get_event to waiting list to recieve js input
        loop = asyncio.get_running_loop()
        empty_future = loop.create_future()

        self.waiting.append(empty_future)

        try:
            return await empty_future
        finally:  # According to ChatGPT, this will prevent memory leak
            if empty_future in self.waiting: self.waiting.remove(empty_future)