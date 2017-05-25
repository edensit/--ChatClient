import socket
import struct


class RegisterStateEnum:
    CORRECT_REGISTER = 1
    INCORRECT_REGISTER = 2


class BaseError(Exception):
    pass


class RegisterError(BaseError):
    pass


class RegisterHandler:
    def __init__(self):
        self.HOST = "127.0.0.1"
        self.PORT = 8820
        self.client_socket = socket.socket()
        self.BUFFER = 1024

    def re_establish_socket(self):
        self.client_socket.close()
        client_socket = socket.socket()
        self.client_socket = client_socket

    def establish_socket(self):
        try:
            self.client_socket.connect((self.HOST, self.PORT))
        except socket.error:
            self.re_establish_socket()

    def incorrect_register_handler(self):
        self.re_establish_socket()

    def send_register_details(self, username, password):
        register_details = username + ":::" + password
        st = struct.pack('!II', 2, 0) + register_details
        try:
            self.client_socket.send(st)
        except socket.error:
            self.re_establish_socket()

    def register_handler(self, username, password):
        self.establish_socket()
        self.send_register_details(username, password)

        try:
            recv_data = self.client_socket.recv(self.BUFFER)
            (d_type,), data = struct.unpack("!I", recv_data[:4]), recv_data[4:]
        except socket.error:
            self.re_establish_socket()
            raise RegisterError("Connection Error")
        else:
            if d_type == RegisterStateEnum.CORRECT_REGISTER:
                return RegisterStateEnum.CORRECT_REGISTER
            elif d_type == RegisterStateEnum.INCORRECT_REGISTER:
                return RegisterStateEnum.INCORRECT_REGISTER
