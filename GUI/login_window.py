import ttk
from Tkinter import *
try:
    from PIL import ImageTk, Image
except ImportError:
    import pip
    pip.main(['install', "pillow"])
    from PIL import ImageTk, Image
from socks import login_handling
import main_window


class LOGIN_ENUM:
    CORRECT_AUTH = 1
    INCORRECT_AUTH = 2
    ALREADY_CONNECTED = 3


class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.login_handler = login_handling.LoginHandler()

        self.master.title("eVoice Chat Client v0.1")
        self.master.geometry("300x400")  # window size
        self.master.resizable(width=False, height=False)

        self.style = ttk.Style()
        self.style.configure("BW.TLabel", foreground="black", background="white")

        self.img = ImageTk.PhotoImage(Image.open("GUI\mainLogo.png"))
        self.logo = ttk.Label(self.master, image=self.img)
        self.logo.pack(side="top", fill="both", expand="yes", padx=22)

        self.username_input = StringVar()
        self.username_frame = ttk.LabelFrame(self.master, text="Username", padding="2")
        self.username_frame.pack(padx=10, pady=10)

        self.username_entry = ttk.Entry(self.username_frame, textvariable=self.username_input)
        self.username_entry.pack()
        self.username_entry.focus_set()

        self.password_input = StringVar()  # Password variable
        self.password_frame = ttk.LabelFrame(self.master, text="Password", relief="ridge", borderwidth=2, padding="2")
        self.password_frame.pack(padx=10, pady=10)

        self.password_entry = ttk.Entry(self.password_frame, textvariable=self.password_input, show='*')
        self.password_entry.pack()

        self.incorrect_l = Label(self.master, text="", fg="red")
        self.incorrect_l.pack()

        self.connect_button = ttk.Button(self.master, text='Connect', command=self.login)
        self.connect_button.pack(expand=False, padx=15, pady=10)

        self.username_entry.bind("<KeyRelease-Return>", lambda e: self.login())
        self.password_entry.bind("<KeyRelease-Return>", lambda e: self.login())

        self.connect_button = ttk.Button(self.master, text='Register', command=self.register)
        self.connect_button.pack(expand=False, padx=15, pady=10)

    def handle_correct_auth(self):
        new_window = Toplevel(self.master)
        main_window.MainWindow(new_window, self.username_input.get())
        self.master.withdraw()

    def handle_incorrect_auth(self):
        self.incorrect_l.config(text="Incorrect username or password!")

    def handle_already_connected(self):
        self.incorrect_l.config(text="Client already connected from another PC")

    def handle_socket_error(self):
        self.incorrect_l.config(text="Connection Error")

    def login(self):
        try:
            d_type = self.login_handler.handle_login(self.username_input.get(), self.password_input.get())
        except login_handling.LoginError as error:
            self.incorrect_l.config(text=error)
        else:
            if d_type == LOGIN_ENUM.CORRECT_AUTH:
                self.handle_correct_auth()
                self.login_handler.handle_correct_auth()

            elif d_type == LOGIN_ENUM.INCORRECT_AUTH:
                self.handle_incorrect_auth()
                self.login_handler.handle_incorrect_auth()

            elif d_type == LOGIN_ENUM.ALREADY_CONNECTED:
                self.handle_already_connected()
                self.login_handler.handle_already_connected()

    def register(self):
        pass