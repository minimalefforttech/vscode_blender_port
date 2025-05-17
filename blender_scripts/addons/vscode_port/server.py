# Copyright (c) 2025 Alex Telford. All rights reserved.
import socket
import logging
import time
from enum import Enum

LOG = logging.getLogger(__name__)

class ReadState(Enum):
    WAITING = "waiting"
    MESSAGE = "message"
    DISCONNECTED = "disconnected"
    ERROR = "error"

class VSCodePortServer:
    _instance = None

    def __init__(self):
        self._server_socket = None
        self._client_socket = None
        self._client_address = None
        self._is_connected = False
    
    def is_connected(self):
        return self._is_connected
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = VSCodePortServer()
        return cls._instance

    def start(self, port):
        if self._server_socket:
            if port == self._server_socket.getsockname()[1]:
                return
            self.stop()
        LOG.debug(f"[VSCodePort] Starting server on port {port}")
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(("localhost", port))
        self._server_socket.listen(1)
        self._server_socket.setblocking(False)
        LOG.debug(f"[VSCodePort] Blender socket server listening on port {port}")

    def stop(self):
        LOG.debug("[VSCodePort] Stopping server...")
        self._cleanup_client_connection()
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception as e:
                LOG.error(f"[VSCodePort] Error closing server socket: {e}")
            self._server_socket = None

    def _cleanup_client_connection(self):
        if self._client_socket:
            try:
                self._client_socket.close()
            except Exception as e:
                LOG.error(f"[VSCodePort] Error closing client socket: {e}")
            self._client_socket = None
            self._is_connected = False
            self._client_address = None

    def accept_client(self):
        client_connection, client_address = self._server_socket.accept()
        client_connection.setblocking(False)
        self._client_socket = client_connection
        self._client_address = client_address
        self._is_connected = True
        LOG.debug(f"[VSCodePort] Accepted connection from {client_address}")

    def read(self, timeout_msecs=5000):
        if not self._client_socket:
            return None, ReadState.DISCONNECTED

        start_time = time.time()
        timeout = timeout_msecs / 1000

        try:
            data = b""
            while True:
                try:
                    chunk = self._client_socket.recv(4096)
                except BlockingIOError:
                    # No data available yet on non-blocking socket
                    return None, ReadState.WAITING
                if not chunk:
                    self._cleanup_client_connection()
                    return None, ReadState.DISCONNECTED

                data += chunk

                if len(data) >= 8:
                    expected_len = int(data[:8].decode())
                    if len(data) >= expected_len + 8:
                        message = data[8:expected_len+8].decode()
                        return message, ReadState.MESSAGE

                if time.time() - start_time > timeout:
                    return None, ReadState.ERROR
        except Exception as e:
            LOG.error(f"[VSCodePort] Error reading from client: {e}")
            self._cleanup_client_connection()
            return None, ReadState.ERROR

    def send_output(self, output):
        """
        Send output string back to the client using the same length-prefixed protocol.
        """
        if not self._client_socket:
            return
        try:
            data = output.encode("utf-8")
            length_header = str(len(data)).zfill(8).encode("utf-8")
            self._client_socket.sendall(length_header + data)
            LOG.debug(f"[VSCodePort] Output sent to client ({len(data)} bytes)")
        except Exception as e:
            LOG.error(f"[VSCodePort] Error sending output to client: {e}")
