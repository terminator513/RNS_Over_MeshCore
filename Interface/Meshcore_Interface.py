# MIT License - Copyright (c) 2026
# Interface for tunnelling Reticulum traffic over a MeshCore TCP bridge.
#
# Place this file in ~/.reticulum/interfaces and configure it like:
#
# [[MeshCore Interface]]
# type = Meshcore_Interface
# enabled = true
# mode = gateway
# host = 127.0.0.1
# port = 9000
#
# The bridge protocol is length-prefixed binary frames:
# [2-byte big-endian length][payload bytes]

from RNS.Interfaces.Interface import Interface
import socket
import threading
import time


class MeshCoreInterface(Interface):
    DEFAULT_IFAC_SIZE = 8

    owner = None

    def __init__(self, owner, configuration):
        super().__init__()

        ifconf = Interface.get_config_obj(configuration)
        self.name = ifconf["name"]

        self.host = ifconf["host"] if "host" in ifconf else "127.0.0.1"
        self.port = int(ifconf["port"]) if "port" in ifconf else 9000
        self.connect_timeout = float(ifconf["connect_timeout"]) if "connect_timeout" in ifconf else 8.0
        self.reconnect_delay = float(ifconf["reconnect_delay"]) if "reconnect_delay" in ifconf else 3.0

        # Mesh mediums are usually constrained, keep MTU conservative.
        self.HW_MTU = int(ifconf["mtu"]) if "mtu" in ifconf else 512
        self.bitrate = int(ifconf["bitrate"]) if "bitrate" in ifconf else 2000

        self.owner = owner
        self.online = False
        self.socket = None
        self._shutdown = False

        self._write_lock = threading.Lock()

        self._connect_thread = threading.Thread(target=self._connect_loop)
        self._connect_thread.daemon = True
        self._connect_thread.start()

    def _connect_loop(self):
        while not self._shutdown:
            if self.socket is None:
                try:
                    self.open_interface()
                    self.online = True
                    RNS.log(f"MeshCore: Connected to {self.host}:{self.port}", RNS.LOG_INFO)
                    self._start_reader()
                except Exception as e:
                    self.online = False
                    self.close_interface()
                    RNS.log(f"MeshCore: Connection failed ({e}), retrying in {self.reconnect_delay}s", RNS.LOG_ERROR)
                    time.sleep(self.reconnect_delay)
            else:
                time.sleep(0.2)

    def _start_reader(self):
        thread = threading.Thread(target=self._read_loop)
        thread.daemon = True
        thread.start()

    def open_interface(self):
        sock = socket.create_connection((self.host, self.port), timeout=self.connect_timeout)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(1.0)
        self.socket = sock

    def close_interface(self):
        sock = self.socket
        self.socket = None
        if sock is not None:
            try:
                sock.close()
            except Exception:
                pass

    def _read_exact(self, n):
        buf = b""
        while len(buf) < n and not self._shutdown:
            if self.socket is None:
                raise ConnectionError("socket closed")
            try:
                chunk = self.socket.recv(n - len(buf))
            except socket.timeout:
                continue

            if not chunk:
                raise ConnectionError("connection closed by peer")
            buf += chunk
        return buf

    def _read_loop(self):
        try:
            while not self._shutdown and self.socket is not None:
                header = self._read_exact(2)
                size = int.from_bytes(header, byteorder="big", signed=False)
                if size == 0:
                    continue
                packet = self._read_exact(size)

                self.rxb += len(packet)
                self.owner.inbound(packet, self)
        except Exception as e:
            if not self._shutdown:
                RNS.log(f"MeshCore: Reader stopped ({e}), reconnecting", RNS.LOG_ERROR)
        finally:
            self.online = False
            self.close_interface()

    def process_outgoing(self, data):
        frame = len(data).to_bytes(2, byteorder="big", signed=False) + data
        with self._write_lock:
            if self.socket is None:
                return
            try:
                self.socket.sendall(frame)
                self.txb += len(data)
            except Exception as e:
                RNS.log(f"MeshCore: Write failed ({e}), reconnecting", RNS.LOG_ERROR)
                self.online = False
                self.close_interface()

    def detach(self):
        self._shutdown = True
        self.online = False
        self.close_interface()

    @staticmethod
    def should_ingress_limit():
        return False

    def __str__(self):
        return "MeshCoreInterface[" + self.name + "]"


interface_class = MeshCoreInterface
