# Caleb Hofschneider SLVROV 12/2024

import struct
from .misc_tools import at_exit


class Joystick:  # ONLY WORKS WITH LINUX!!!!!!!
        """
        Class with methods allowing access to joystick input on Rapsberry Pi computers

        Attributes:
            path (str): name of joystick input file; can be found is /dev/input/
            device (_io.BufferReader): joystick input file opened with read bytes
            buttons (list): list of all button states - state indices correspond with button numbers
            axis (list): list of all axis states - state indices correspond with axis numbers
            axis_funcs (list or tuple): list of functons corresponding with axis; functions should take axis event value as argument
            button_funcs (list or tuple): list of functons corresponding with buttons; functions should button event value as argument
            packet_size (int): size of input packets in bytes
            data_format (str): struct format of joystick input - https://docs.python.org/3/library/struct.html#format-characters for more formats

        Methods:
            get_event(): reads event data from self.device
            interpret_event(event, axis_code, button_code): logs event values in Joystick.axis or Joystick.buttons
            init(packet_num, process_packets): Handles any initial or "set-up" packets sent from joystick, usually data about joystick current position etc.
            restart_read(): reopens Joystick.device file
            terminate_read(): closes Joystick.device file
            execute_events(): executes axis and buttons functions (accessed in Joystick.axis_funcs and Joystick.button_funcs) using for loop
        """

        def __init__(self, path, axis_funcs, button_funcs, num_of_axis, num_of_buttons, packet_size=8, data_format="IhBB"):
            """
            Initializes Joystick object attributes.

            Arguments:
                path (str): name of joystick input file; can be found is /dev/input/
                axis_funcs (list or tuple): list of functons corresponding with axis; functions should take axis event value as argument
                button_funcs (list or tuple): list of functons corresponding with buttons; functions should button event value as argument
                num_of_buttons (int): number of buttons on joystick
                num_of_axis (int): number of axis on joystick
                packet_size (int): size of packets from joystick in bytes; set to 8 by default
                data_format (str): struct format of joystick input; set to "IhBB" by default - https://docs.python.org/3/library/struct.html#format-characters for more formats
            """
            
            self.path = path

            self.device = open(f"/dev/input/{path}", "rb")

            self.buttons = [0 for _ in range(num_of_buttons)]
            self.axis = [0 for _ in range(num_of_axis)]

            self.axis_funcs = axis_funcs
            self.button_funcs = button_funcs

            self.packet_size = packet_size
            self.data_format = data_format

            at_exit(self.terminate_read)

        def get_event(self):
            """
            Reads event data from Joystick.device (joystick device input file).

            Takes no arguments (other than self object)

            Returns:
                time (int): elapsed time since event
                typ (int): event type - usually 2 is axis event, 1 is button event
                number (int): axis/button number
                value (int): values of event (button 1/0, and axis vector)
            """

            input_data = self.device.read(self.packet_size)
            time, value, typ, number = struct.unpack(self.data_format, input_data)

            return time, typ, number, value

        def interpret_event(self, event, axis_code=2, button_code=1):
            """
            Logs event values in Joystick.axis or Joystick.buttons.

            Arguments:
                event (list or tuple): list of type, number, and value data
                axis_code (int): type value which indicates axis data; this is usually 2, so is set to 2 by default
                button_code (int): type value which indicates button data; this is usually 1, so is set to 1 by default

                EVENT TYPES MAY CHANGE WHEN JOYSTICK IS SENDING INITIAL VALUES - UPDATE axis_code AND button_code ACCORDINGLY
            """
            
            if event[0] == axis_code:
                self.axis[event[1]] = -event[2]
            elif event[0] == button_code:
                self.buttons[event[1]] = event[2]
            else:
                raise Exception(f"{event[0]} -- Invalid Event Type")

        def init(self, packet_num, axis_code=130, button_code=129, process_packets=False):
            """
            Handles any initial or "set-up" packets sent from joystick, usually data about joystick current position etc.

            Arguments:
                packet_num (int): number of packets to process; number of initial packets sent over by joystick
                axis_code (int): type value which indicates axis data in the initial packets - this might be different than the usual type values
                button_code (int): type value which indicates button data in the initial packets - this might be different than the usual type values
                process_packets (bool): indicates whether to save and execute initial packet instructions; set to False by default for safety
            """
            
            packet_count = 0

            while packet_count < packet_num:
                _, *event = self.get_event()

                if process_packets:
                    self.interpret_event(event, axis_code, button_code)

                packet_count += 1

            if process_packets:
                self.execute_events()

        def restart_read(self):
            """
            Opens joystick input file as Joystick.device. 
            This is only used when the file is needed again after closing it: __init__ method opens input file automatically at object assignment.
            """

            self.device = open(f"/dev/input/{self.path}")

        def terminate_read(self):
            """
            Closes Joystick.device file.
            THIS NEEDS TO HAPPEN WHENEVER JOYSTICK DATA NO LONGER NEEDS TO BE READ.
            """
            
            self.device.close()

        def execute_events(self):
            """
            Executes each event by iterating through Joystick.axis and Joystick.buttons and running their corresponding functions.
            This is done using for loops, so it will slow down the update loop for longer axis/button functions.
            """
            
            for event in self.axis:
                self.axis_funcs[self.axis.index(event)](event)
            for event in self.buttons:
                self.button_funcs[self.buttons.index(event)](event)