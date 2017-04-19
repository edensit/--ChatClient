import socket
import thread
import struct
import Queue


class SEND_ENUM:
    TYPE_LOGIN = 1
    TYPE_REGISTER = 2
    TYPE_MSG = 3
    TYPE_COMMAND = 4
    TYPE_POKE = 5


class RECV_ENUM:
    TYPE_MSG = 1
    TYPE_USER_LIST = 2
    TYPE_POKE = 3


class BaseError(Exception):
    pass


class ConnectionError(BaseError):
    pass


class EmptyMessagesQError(BaseError):
    pass


class SockHandler:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.BUFFER = 1024
        thread.start_new_thread(self.receive_data, ())
        self.received_messages = Queue.Queue()

    def get_next_message(self):
        try:
            return self.received_messages.get(True, 5)
        except Queue.Empty:
            raise EmptyMessagesQError()

    @staticmethod
    def pack_data(d_type, arg, data):
        return struct.pack('!II', d_type, arg) + data

    def send_msg(self, data, d_type=SEND_ENUM.TYPE_MSG, arg=0):
        packed_data = self.pack_data(d_type, arg, data)

        if len(data) >= 1 and d_type == SEND_ENUM.TYPE_MSG:
            try:
                self.client_socket.send(packed_data)
            except socket.error:
                raise ConnectionError("Connection Error")

            finally:
                pass

        elif d_type != SEND_ENUM.TYPE_MSG:
            try:
                self.client_socket.send(packed_data)
            except socket.error:
                raise ConnectionError("Connection Error")

    def receive_data(self):
        while True:
            try:
                recv_data = self.client_socket.recv(self.BUFFER)
            except socket.error:
                self.client_socket.close()
                raise ConnectionError("Connection Error")
            else:
                (d_type,), data = struct.unpack("!I", recv_data[:4]), recv_data[4:]
                self.received_messages.put((d_type, data))

    def close_socket(self):
        self.client_socket.close()
