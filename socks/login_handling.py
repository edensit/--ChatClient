import socket
import struct
from socks import sock_handling


class LOGIN_ENUM:
    CORRECT_AUTH = 1
    INCORRECT_AUTH = 2
    ALREADY_CONNECTED = 3


class BaseError(Exception):
    pass


class LoginError(BaseError):
    pass


class LoginHandler:
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

    def get_sock(self):
        return self.client_socket

    def handle_correct_auth(self):
        pass

    def handle_incorrect_auth(self):
        self.re_establish_socket()

    def handle_already_connected(self):
        self.re_establish_socket()

    def send_login_auth(self, username, password):
        login_auth = username + ":::" + password
        st = struct.pack('!II', 1, 0) + login_auth
        try:
            self.client_socket.send(st)
        except socket.error:
            self.re_establish_socket()

    def handle_login(self, username, password):
        self.establish_socket()
        self.send_login_auth(username, password)

        try:
            recv_data = self.client_socket.recv(self.BUFFER)
            (d_type,), data = struct.unpack("!I", recv_data[:4]), recv_data[4:]
        except socket.error:
            self.re_establish_socket()
            raise LoginError("Connection Error")
        else:
            if d_type == LOGIN_ENUM.CORRECT_AUTH:
                return LOGIN_ENUM.CORRECT_AUTH
            elif d_type == LOGIN_ENUM.INCORRECT_AUTH:
                return LOGIN_ENUM.INCORRECT_AUTH
            elif d_type == LOGIN_ENUM.ALREADY_CONNECTED:
                return LOGIN_ENUM.ALREADY_CONNECTED
