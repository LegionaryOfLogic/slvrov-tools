# Caleb Hofschneider SLV ROV 5/2025

import socket
from concurrent.futures import ThreadPoolExecutor
from .misc_tools import at_exit
from typing import Callable

protocols_by_transport = {
            "raw": socket.SOCK_RAW,

            "tcp": socket.SOCK_STREAM,
            "http": socket.SOCK_STREAM,
            "https": socket.SOCK_STREAM,
            "ftp": socket.SOCK_STREAM,
            "smtp": socket.SOCK_STREAM,
            "imap": socket.SOCK_STREAM,
            "pop3": socket.SOCK_STREAM,
            "ssh": socket.SOCK_STREAM,
            "telnet": socket.SOCK_STREAM,
            "bgp": socket.SOCK_STREAM,
            "irc": socket.SOCK_STREAM,
            "ldap": socket.SOCK_STREAM,
            "smb": socket.SOCK_STREAM,
            "rdp": socket.SOCK_STREAM,
            "nntp": socket.SOCK_STREAM,

            "udp": socket.SOCK_DGRAM,
            "dhcp": socket.SOCK_DGRAM,
            "tftp": socket.SOCK_DGRAM,
            "snmp": socket.SOCK_DGRAM,
            "ntp": socket.SOCK_DGRAM,
            "rip": socket.SOCK_DGRAM,
            "rtp": socket.SOCK_DGRAM,
            "syslog": socket.SOCK_DGRAM,
            "mdns": socket.SOCK_DGRAM,
            "llmnr": socket.SOCK_DGRAM,

            "quic": socket.SOCK_DGRAM}


class Network_Communicator:
    """
    A class to manage socket-based communication using multithreading, with protocol abstraction for various common 
    network protocols. Designed for both connection-oriented (TCP) and connectionless (UDP) communication patterns.

    Attributes:
        IP (str): Local IP address the socket binds to.
        port (int): Local port number to bind the socket to.
        protocols_by_transport (dict): Mapping of protocol names (e.g., 'tcp', 'udp', 'http') to socket types.
        protocol (str): The specified protocol in lowercase, used to resolve socket type.
        communication_type (int): Socket type (e.g., socket.SOCK_STREAM) based on protocol.
        packet_handler (Callable): Function used to handle received packets. Defaults to an internal test handler.
        recieved_count (int): Counter tracking the number of packets received when using the test handler.
        socket (socket.socket): The underlying bound socket object.
        bound (bool): Boolean flag indicating if the socket is currently open and bound.
        to_IP (str): Remote IP address to connect to (used in client mode).
        to_port (int): Remote port number to connect to.
        connected (bool): Flag indicating if a connection to a remote host is active.
        executor (ThreadPoolExecutor): Thread pool used to spawn packet handler threads.

    Key Methods:
        connect_to(to_IP, to_port) -> None: Establishes a connection to a remote IP and port.
        disconnect() -> None: Disconnects from the remote endpoint by nulling the connection.
        reconnect() -> None: Re-establishes the most recent connection (after disconnect).
        spawn_handler_thread(*args) -> None: Spawns a thread to handle incoming packet data using the assigned handler.
        set_socket() -> socket.socket: Creates and binds a socket with the specified communication type.
        open(IP=None, port=None) -> None: Opens (or re-opens) the socket on the given or previous IP/port.
        close() -> None: Closes the socket if currently bound.
        test_packet_handler(*args) -> str: Default handler that prints packet details and increments `recieved_count`.
    """

    def __init__(self, IP: str, port: int, protocol: str, packet_handler: Callable | str="test", max_threads: int=10):
        """
        Initializes the network communicator with socket parameters.

        Args:
            IP (str): Local IP address to bind to.
            port (int): Local port to bind to.
            protocol (str): Protocol name (e.g., 'tcp', 'udp', 'http').
            packet_handler (Callable | str): Handler for incoming packets or 'test' for default.
            max_threads (int): Maximum number of handler threads, set to 10 as default
        """

        global protocols_by_transport

        self.IP = IP
        self.port = port

        self.protocols_by_transport = protocols_by_transport
        self.protocol = protocol.strip().lower()
        self.communication_type = self._resolve_comm_type()

        if packet_handler == "test": self.packet_handler = self.test_packet_handler
        else: self.packet_handler = packet_handler
        self.recieved_count = 0

        self.socket = self.set_socket()
        self.bound = True

        self.to_IP = None
        self.to_port = None
        self.connected = False

        self.executor = ThreadPoolExecutor(max_workers=max_threads)

        at_exit(self.close)

    def test_packet_handler(self, *args) -> str:
        """
        Default packet handler used for testing. Prints information about the packet just recieved.
        
        Args:
            *args: Tuple of (data, address) or just (data,) depending on protocol context.

        Returns:
            description (str): information printed about recieved packet

        Raises:
            Exception: If len(args) is not 1 or 2
        """

        if len(args) == 2:
            data, address = args
            description = f"{self.recieved_count}\tRecieved {len(data)} bytes from port {address[1]} on {address[0]}"
        elif len(args) == 1:
            description = f"{self.recieved_count}\tRecieved {len(data)} bytes from {self.to_IP}"
        else: raise Exception("Internal Error: Test handler not functioning correctly")

        print(description)
        return description

    def _resolve_comm_type(self):
        """
        Resolves the socket type from the protocol string.

        Returns:
            int: Socket type (e.g., socket.SOCK_STREAM).

        Raises:
            Exception: If protocol is not supported.
        """

        try:
            return self.protocols_by_transport[self.protocol]
        except KeyError:
            raise Exception("Unsupported protocol. Select valid from .protocols_by_transport or resort to primitive types 'udp', 'tcp' and 'raw'")

    def connect_to(self, to_IP: str, to_port: int) -> None:
        """
        Connects the socket to a remote IP and port.

        Args:
            to_IP (str): Destination IP address.
            to_port (int): Destination port number.
        """

        self.to_IP = to_IP
        self.to_port = to_port

        self.socket.connect((to_IP, to_port))
        self.connected = True

    def disconnect(self) -> None:
        """
        Disconnects from the current remote endpoint by connecting to a null address.
        """

        self.socket.connect(("0.0.0.0", 0))
        self.connected = False

    def reconnect(self) -> None:
        """
        Reconnects to the most recent remote IP and port (set using the 'connect' method) after disconnect
        """

        self.socket.connect((self.to_IP, self.to_port))
        self.connected = True

    def spawn_handler_thread(self, *arguments) -> None:
        """
        Spawns a new thread to handle packets using the packet_handler.

        Args:
            *arguments: Arguments to pass to the packet handler function.
        """

        self.executor.submit(self.packet_handler, *arguments)

    def set_socket(self) -> socket.socket:
        """
        Creates and binds a socket to the specified local IP and port.

        Returns:
            self.socket (socket.socket): The bound socket object.
        """

        self.socket = socket.socket(socket.AF_INET, self.communication_type)
        self.socket.bind((self.IP, self.port))

        self.bound = True
        return self.socket

    def close(self) -> None:
        """
        Closes the local socket if it is currently bound.
        """

        if self.bound:
            self.socket.close()
            self.bound = False

    def open(self, IP: str=None, port: int=None) -> None:
        """
        Opens a local socket with provided IP/port or reopens the socket using last bound IP/port.

        Args:
            IP (str, optional): New IP address to bind to.
            port (int, optional): New port number to bind to.
        """

        if IP is not None and port is not None: 
            self.IP = IP
            self.port = port

        self.set_socket()


# Caleb Hofschneider SLV ROV 5/2025

from typing import Callable, List

class UDP_Communicator(Network_Communicator):
    """
    A specialized subclass of Network_Communicator for handling UDP-based network communication.

    This communicator supports sending and receiving UDP packets using both connected and unconnected socket modes.
    It inherits threading, socket setup, and packet handling from the base class and adds UDP-specific transmission 
    and reception capabilities.

    Attributes:
        IP (str): Local IP address to bind to.
        port (int): Local port number for communication.
        protocol (str): Always set to 'udp' for this subclass.
        packet_handler (Callable): Function used to process received packets.
        recieved_count (int): Counter that tracks how many packets have been received.
        socket (socket.socket): The UDP socket object used for communication.
        connected (bool): Indicates if the socket is connected to a specific remote host.
        executor (ThreadPoolExecutor): Thread pool used to execute packet handler functions concurrently.

    Key Methods:
        sendto(data, to_IP, to_port) -> None:
            Sends a UDP packet to a specific remote IP and port.

        send(data) -> None:
            Sends a UDP packet using a previously connected socket.

        send_queue(data, IP="", port=-1) -> None:
            Sends multiple UDP packets either to a connected host or to a provided destination.

        recieve_all(count="continual", buffer_size=1521, threaded=False) -> None:
            Listens for incoming packets from any address and optionally handles them in threads.

        recieve_from(IP=None, port=None, count="continual", buffer_size=1521, threaded=False) -> None:
            Receives packets from a specific IP/port or a connected host, using a packet handler that 
            accepts only the raw data.
    """

    def __init__(self, IP: str, port: int, packet_handler: Callable | str="test", max_threads: int=10):
        """
        Initializes the UDP_Communicator with a bound UDP socket and packet handler.

        Args:
            IP (str): The local IP address to bind the socket to.
            port (int): The local port number to bind the socket to.
            packet_handler (Callable): Function to handle received packets.
            max_threads (int, optional): Maximum number of threads for handling packets. Defaults to 10.
        """
        
        super().__init__(IP=IP, port=port, packet_handler=packet_handler, protocol="udp", max_threads=max_threads)

    def sendto(self, data: bytes | bytearray, to_IP: str, to_port: int) -> None:
        """
        Sends a UDP packet to a specific destination IP and port.

        Args:
            data (bytes | bytearray): The packet data to send.
            to_IP (str): The target IP address.
            to_port (int): The target port number.
        """

        self.socket.sendto(data, (to_IP, to_port))

    def send(self, data: bytes | bytearray) -> None:
        """
        Sends a UDP packet using the connected socket.

        This method assumes that the socket has already been connected using `connect_to`.

        Args:
            data (bytes | bytearray): The packet data to send.

        Raises:
            Exception: If the socket is not connected.
        """
        
        if not self.connected: raise Exception("Must connect using 'connect_to' method in order to use this")
        self.socket.send(data)

    def send_queue(self, data: List[bytes | bytearray], IP: str="", port: int=-1) -> None:
        """
        Sends a sequence of UDP packets either to a connected peer or to the specified destination.

        If the communicator is connected, packets are sent using the `send` method.
        Otherwise, a destination IP and port must be provided to use `sendto`.

        Args:
            data (List[bytes | bytearray]): A list of packet data to send.
            IP (str, optional): Target IP address if not connected. Defaults to "".
            port (int, optional): Target port if not connected. Defaults to -1.

        Raises:
            Exception: If no connection is active and no destination IP/port is provided.
        """
        
        if self.connected:
            for item in data:
                self.send(item)

        else:
            if IP == "" or port == -1: raise Exception("Please provide IP and port or connect")

            for item in data:
                self.sendto(data=item, to_IP=IP, to_port=port)

    def recieve_all(self, count: int | str="continual", buffer_size: int=1472, threaded: bool=False) -> None:
        """
        Recieves packets from the socket\n
        NOTE: Packet handler must be configured to accept a bytes 'data' AND an str 'address' argument\n
        NOTE: This communicator will disconnect from any connected peers to recieve using this function

        Args:
            count (int, optional): How many packets revice_from should handle before exiting. Default is "continual" for continuous recieving
            buffer_size (int, optional): The largest packet (in bytes) that can be recieved. Default is 1472
            threaded (bool, optional): Threads will be spawned if true. Default is False

        Raises:
            Exception: If an error occurs while receiving data. The socket will be closed.
        """

        if self.connected: 
            was_connected = True
            self.disconnect()
        else: was_connected = False

        if count == "continual":
            try:
                while True:
                    data, addr = self.socket.recvfrom(buffer_size)
                    self.recieved_count += 1

                    if threaded: self.spawn_handler_thread(data, addr)
                    else: self.packet_handler(data, addr)

            finally:
                self.socket.close()
                raise Exception("Error thrown. Socket closed")

        else:
            for _ in range(count):
                data, addr = self.socket.recvfrom(buffer_size)
                self.recieved_count += 1

                if threaded: self.spawn_handler_thread(data, addr)
                else: self.packet_handler(data, addr)

            if was_connected: self.reconnect()

    def recieve_from(self, IP: str=None, port: int=None, count: int | str="continual", buffer_size: int=1472, threaded: bool=False) -> None:
        """
        Recieves packets from a specified or connected IP address and port\n
        NOTE: Packet handler must be configured to accept ONLY a bytes 'data' argument

        Args:
            IP (str, optional): IP address to connect to. Defaults to connected socket IP if None. Is set to None by default
            port (int, optional): Port number to connect to. Defaults to connected socket port if None. Is set to None by default
            count (int | str, optional): Number of packets to receive. Use "continual" to receive indefinitely. Is "continual" by default
            buffer_size (int, optional): Maximum size of each packet in bytes. Defaults to 1472.
            threaded (bool, optional): If True, each packet is handled in a separate thread. Defaults to False.

        Raises:
            Exception: If no destination is provided and was not connected using the 'connect_to' or 'reconnect' methods
            Exception: If an error occurs during packet reception. The socket will be closed.
        """

        if IP is not None: self.connect_to(to_IP=IP, to_port=port)
        else:
            if self.connected is None or not self.connected: raise Exception("Please provide IP and port")

        if count == "continual":
            try:
                while True:
                    data = self.socket.recv(buffer_size)
                    self.recieved_count += 1

                    if threaded: self.spawn_handler_thread(data)
                    else: self.packet_handler(data)
                    
            finally:
                self.socket.close()
                raise Exception("Error thrown. Socket closed")

        else:
            for _ in range(count):
                data = self.socket.recv(buffer_size)
                self.recieved_count += 1
                
                if threaded: self.spawn_handler_thread(data)
                else: self.packet_handler(data)