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
import register_window


class LoginAuthStateEnum:
    CORRECT_AUTH = 1
    INCORRECT_AUTH = 2
    ALREADY_CONNECTED = 3


class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.login_handler = login_handling.LoginHandler()

        self.master.title("eVoice Chat Client v0.1")
        self.master.geometry("300x400")
        self.master.resizable(width=False, height=False)

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

        self.connect_button = ttk.Button(self.master, text='Connect', command=self.login)
        self.connect_button.pack(expand=False, padx=15, pady=10)

        self.username_entry.bind("<KeyRelease-Return>", lambda e: self.login())
        self.password_entry.bind("<KeyRelease-Return>", lambda e: self.login())

        self.connect_button = ttk.Button(self.master, text='Register', command=self.register)
        self.connect_button.pack(expand=False, padx=15, pady=10)

    def correct_auth_handler(self):
        sock = self.login_handler.get_sock()
        new_window = Toplevel(self.master)
        main_window.MainWindow(new_window, self.username_input.get(), sock)
        self.master.withdraw()

    def incorrect_auth_handler(self):
        self.incorrect_l.config(text="Incorrect username or password!")

    def already_connected_handler(self):
        self.incorrect_l.config(text="Client already connected from another PC")

    def socket_error_handler(self):
        self.incorrect_l.config(text="Connection Error")

    def toggle_busy_cursor(self):
        if self.master.cget("cursor") == "":
            self.master.config(cursor="wait")
        else:
            self.master.config(cursor="")
        self.master.update()

    def login(self):
        try:
            self.toggle_busy_cursor()
            d_type = self.login_handler.login_handler(self.username_input.get(), self.password_input.get())
        except login_handling.LoginError as error:
            self.incorrect_l.config(text=error)
        else:
            if d_type == LoginAuthStateEnum.CORRECT_AUTH:
                self.correct_auth_handler()
                # self.register_handler.handle_correct_auth()
            elif d_type == LoginAuthStateEnum.INCORRECT_AUTH:
                self.incorrect_auth_handler()
                self.login_handler.incorrect_auth_handler()
            elif d_type == LoginAuthStateEnum.ALREADY_CONNECTED:
                self.already_connected_handler()
                self.login_handler.already_connected_handler()
        finally:
            self.toggle_busy_cursor()

    def register(self):
        new_window = Toplevel(self.master)
        register_window.RegisterWindow(new_window)
        self.master.withdraw()

"""
        self.style = ttk.Style()
        #self.style.theme_use('clam')
        #self.style.configure('TMenubutton', background=self.master.cget("bg")) # style="TMenubutton"
        print self.style.theme_use()
"""