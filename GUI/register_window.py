import ttk
from Tkinter import *
try:
    from PIL import ImageTk, Image
except ImportError:
    import pip
    pip.main(['install', "pillow"])
    from PIL import ImageTk, Image
from socks import register_handling
import main_window


class RegisterStateEnum:
    CORRECT_REGISTER = 1
    INCORRECT_REGISTER = 2
    ILLEGAL_USERNAME = 3
    ILLEGAL_PASSWORD = 4


class RegisterWindow:
    def __init__(self, master):
        self.master = master
        self.register_handler = register_handling.RegisterHandler()

        self.master.title("eChat Chat Client v1.0")
        self.master.geometry("300x400")  # window size
        self.master.resizable(width=False, height=False)

        self.style = ttk.Style()

        self.img = ImageTk.PhotoImage(Image.open("GFX\main_logo.png"))
        self.logo = ttk.Label(self.master, image=self.img)
        self.logo.pack(side="top", fill="both", expand="yes", padx=22)

        self.username_input = StringVar()
        self.username_frame = ttk.LabelFrame(self.master, text="Username", padding="2")
        self.username_frame.pack(padx=10, pady=10)

        self.username_entry = ttk.Entry(self.username_frame, textvariable=self.username_input)
        self.username_entry.pack()
        self.username_entry.focus_set()

        self.password_input = StringVar()
        self.password_frame = ttk.LabelFrame(self.master, text="Password", relief="ridge", borderwidth=2, padding="2")
        self.password_frame.pack(padx=10, pady=10)

        self.password_entry = ttk.Entry(self.password_frame, textvariable=self.password_input, show='*')
        self.password_entry.pack()

        self.incorrect_l = Label(self.master, text="", fg="red")
        self.incorrect_l.pack()

        self.connect_button = ttk.Button(self.master, text='Register', command=self.login)
        self.connect_button.pack(expand=False, padx=15, pady=10)

        self.master.bind("<KeyRelease-Return>", lambda e: self.login())

    def toggle_busy_cursor(self):
        if self.master.cget("cursor") == "":
            self.master.config(cursor="wait")
        else:
            self.master.config(cursor="")
        self.master.update()

    def correct_register_handler(self):
        self.incorrect_l.config(text="You have successfully registered. Please log in.")

    def incorrect_register_handler(self):
        self.incorrect_l.config(text="Username already exists!")

    def illegal_username(self):
        self.incorrect_l.config(text='Username can only contain letters, numbers,\n "-", and "_" and most more then 4 chars')

    def illegal_password(self):
        self.incorrect_l.config(text='Password can only contain letters, numbers,\n "-", and "_" and most more then 8 chars')

    def socket_error_handler(self):
        self.incorrect_l.config(text="Connection Error")

    def login(self):
        try:
            self.toggle_busy_cursor()
            d_type = self.register_handler.register_handler(self.username_input.get(), self.password_input.get())
        except register_handling.RegisterError as error:
            self.incorrect_l.config(text=error)
        else:
            if d_type == RegisterStateEnum.CORRECT_REGISTER:
                self.correct_register_handler()
            elif d_type == RegisterStateEnum.INCORRECT_REGISTER:
                self.incorrect_register_handler()
                self.register_handler.incorrect_register_handler()
            elif d_type == RegisterStateEnum.ILLEGAL_USERNAME:
                self.illegal_username()
                self.register_handler.incorrect_register_handler()
            elif d_type == RegisterStateEnum.ILLEGAL_PASSWORD:
                self.illegal_password()
                self.register_handler.incorrect_register_handler()
        finally:
            self.toggle_busy_cursor()
