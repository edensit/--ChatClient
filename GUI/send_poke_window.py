from Tkinter import *
import ttk


class SendPokeWindow:
    def __init__(self, master, main_window, name):
        self.master = master
        self.name = name
        self.main_window = main_window

        self.master.title("Poke")

        self.width = 190
        self.height = 90

        # get screen width and height
        self.screen_width = self.master.winfo_screenwidth()  # width of the screen
        self.screen_height = self.master.winfo_screenheight()  # height of the screen

        # calculate win_x_coordinates and win_y_coordinates coordinates for the Tk root window
        self.win_x_coordinates = (self.screen_width / 2) - (self.width / 2)
        self.win_y_coordinates = (self.screen_height / 2) - (self.height / 2)

        # set the dimensions of the screen and where it is placed
        self.master.geometry('%dx%d+%d+%d' % (190, 90, self.win_x_coordinates, self.win_y_coordinates))

        self.style = ttk.Style()
        self.style.configure("BW.TLabel", foreground="black", background="white")

        self.poke_input = StringVar()
        self.poke_frame = ttk.LabelFrame(self.master, text="Poke Reason", padding="2")
        self.poke_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=5)

        self.master.grid_columnconfigure(0, weight=0)
        self.master.grid_rowconfigure(0, weight=1)

        self.poke_entry = ttk.Entry(self.poke_frame, textvariable=self.poke_input)
        self.poke_entry.grid(row=1, column=2, columnspan=2)
        self.poke_entry.focus_set()
        self.poke_entry.bind("<KeyRelease-Return>", lambda e: self.send_poke())

        self.send_poke_button = ttk.Button(self.master, text='OK', command=self.send_poke)
        self.send_poke_button.grid(row=3, column=1, padx=10, pady=5)

        self.cancel_button = ttk.Button(self.master, text='Cancel', command=self.master.destroy)
        self.cancel_button.grid(row=3, column=2, padx=10, pady=5)

    def send_poke(self):
        data = self.name + ":::" + self.poke_input.get()
        #self.main_window.send_msg(data, 5)
        self.master.destroy()
