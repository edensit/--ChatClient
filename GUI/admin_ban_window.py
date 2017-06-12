from Tkinter import *
import ttk


class AdminBanWindow:
    def __init__(self, main_window):
        self.master = Toplevel()
        self.main_window = main_window

        self.master.geometry('1100x550')
        self.master.resizable(width=False, height=False)

        self.master.title("Ban Management")

        self.FILES_FRAME = ttk.LabelFrame(self.master, text='Files', height=460, width=890)
        self.FILES_FRAME.place(relx=0, rely=0.001)

        self.COLUMNS = ('Category', 'File', 'Size', 'Uploader', 'Date')
        self.FILES = ttk.Treeview(self.FILES_FRAME, columns=self.COLUMNS, show='headings', height=21)
        FILES_ysb = ttk.Scrollbar(orient=VERTICAL, command=self.FILES.yview)
        xsb = ttk.Scrollbar(orient=HORIZONTAL, command=self.FILES.xview)
        self.FILES['yscroll'] = FILES_ysb.set
        self.FILES['xscroll'] = xsb.set

        self.FILES.grid(row=0, column=0)
        FILES_ysb.grid(in_=self.FILES_FRAME, row=0, column=1, sticky=NS)

