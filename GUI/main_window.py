from Tkinter import *
import ttk
import tkMessageBox
from datetime import datetime
import cPickle
import Queue
import thread
from socks import sock_handling
from GUI import send_poke_window


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


class MainWindow:
    def __init__(self, master, username, sock):
        self.master = master
        self.username = username

        self.sock_handler = sock_handling.SockHandler(sock)

        self.master.title("eVoice Chat Client v0.1")
        self.master.geometry("775x380")  # window size
        self.master.resizable(width=False, height=False)

        self.master.protocol("WM_DELETE_WINDOW", self.handle_closing)

        self.style = ttk.Style()
        self.style.configure("BW.TLabel", foreground="black", background="white")

        ttk.Label(self.master, text="Logged in as " + str(self.username)).grid(row=0, column=0, sticky=W)

        self.user_list_frame = LabelFrame(self.master, text="Online Users", padx=5, pady=5)
        self.user_list_frame.grid(row=1, column=0, sticky=W, columnspan=10, rowspan=20)
        self.user_list = Listbox(self.user_list_frame, width=37, height=20)
        self.user_list.grid()
        self.user_list.bind("<Double-Button-1>", self.on_double_click)

        # user_list Scrollbar
        self.user_list_scroll_b = ttk.Scrollbar(self.user_list_frame, command=self.user_list.yview)
        self.user_list_scroll_b.grid(row=0, column=1, sticky='nsew')
        self.user_list['yscrollcommand'] = self.user_list_scroll_b.set

        self.chat_frame = LabelFrame(self.master, text="Chat Box", padx=5, pady=5)
        self.chat_frame.grid(row=1, column=12, sticky=N, columnspan=10, rowspan=20)
        self.chat_textbox = Text(self.chat_frame, width=60, height=15)
        self.chat_textbox.grid()
        self.chat_textbox.tag_config('RED', foreground='red')
        self.chat_textbox.bind("<Key>", lambda e: "break")  # makes the text box readonly
        self.chat_textbox.bind('<Control-c>', self.copy)

        # chat_textbox Scrollbar
        self.scroll_b = ttk.Scrollbar(self.chat_frame, command=self.chat_textbox.yview)
        self.scroll_b.grid(row=0, column=1, sticky='nsew')
        self.chat_textbox['yscrollcommand'] = self.scroll_b.set

        self.msg_input = StringVar()
        self.msg_box_frame = LabelFrame(self.master, text="MSG Box", padx=5, pady=5)
        self.msg_box_frame.grid(row=20, column=12, sticky=W + S)
        self.msg_box_entry = ttk.Entry(self.msg_box_frame, textvariable=self.msg_input, width=70)
        self.msg_box_entry.grid()
        self.msg_box_entry.bind("<KeyRelease-Return>", lambda e: self.send_msg(self.msg_input.get()))

        self.send_button_frame = LabelFrame(self.master, text="", padx=6, pady=6.4)
        self.send_button_frame.grid(row=20, column=18, sticky=W + S)
        self.send_button = ttk.Button(
            self.send_button_frame, text='Send', command=lambda: self.send_msg(self.msg_input.get()), width=6)
        self.send_button.pack(fill=BOTH, expand=1)

        self.q = Queue.Queue()
        self.master.after(100, self.check_queue)
        thread.start_new_thread(self.received_messages, ())

    def handle_closing(self):
        if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
            self.sock_handler.close_socket()
            self.master.destroy()
            raise SystemExit

    def handle_data(self, data):
        d_type = data[0]
        data = data[1]

        if d_type == RECV_ENUM.TYPE_MSG:
            self.insert_msg(data)
        elif d_type == RECV_ENUM.TYPE_USER_LIST:
            self.update_users_list(data)
        elif d_type == RECV_ENUM.TYPE_POKE:
            self.handle_incoming_poke(data)

    def received_messages(self):
        while True:
            try:
                data = self.sock_handler.get_next_message()
            except sock_handling.EmptyMessagesQError:
                pass
            else:
                self.handle_data(data)

    def check_queue(self):
        while True:
            try:
                task = self.q.get(block=False)
            except Queue.Empty:
                break
            else:
                self.master.after_idle(task)
        self.master.after(100, self.check_queue)

    def copy(self, event=None):
        text = self.chat_textbox.get("sel.first", "sel.last")
        self.chat_textbox.clipboard_append(text)
        # https://mail.python.org/pipermail/tutor/2004-July/030398.html

    def show_poke(self, data):
        username = data[:data.index(":::")]
        msg = data[data.index(":::") + 3:]
        self.chat_textbox.insert(END, "\n%s - %s pokes you: %s" % (datetime.now().strftime('%H:%M:%S'), username, msg))
        tkMessageBox.showinfo("You Have Been Poked", "\n%s - %s pokes you: %s" % (datetime.now().strftime('%H:%M:%S'), username, msg))

    def handle_incoming_poke(self, data):  # d_type 3 - poke
        self.q.put(lambda: self.show_poke(data))

    def insert_msg(self, data):  # d_type 1 - msg
        self.chat_textbox.insert(END, "\n%s %s" % (datetime.now().strftime('%H:%M:%S'), data))
        self.chat_textbox.see(END)

    def update_users_list(self, data):  # d_type 2 - users list
        self.user_list.delete(0, END)
        users_list = cPickle.loads(data)
        for user in users_list:
            self.user_list.insert(END, user)

    def connection_error(self):
        self.chat_textbox.insert(END, "\nConnection to server lost!\n", "RED")
        self.chat_textbox.see(END)

    def send_msg(self, data, d_type=SEND_ENUM.TYPE_MSG, arg=0):
        data = str(data)
        if len(data) >= 1 and d_type == SEND_ENUM.TYPE_MSG:
            try:
                self.chat_textbox.insert(END, "\n%s [Me] %s" % (datetime.now().strftime('%H:%M:%S'), data))
                self.sock_handler.send_msg(data)
            except sock_handling.ConnectionError as error:
                self.chat_textbox.insert(END, "\nError: The message was not delivered", "RED")
            else:
                pass
            finally:
                self.msg_box_entry.delete(0, 'end')
                self.chat_textbox.see(END)
                self.msg_box_entry.focus_set()
        elif d_type != SEND_ENUM.TYPE_MSG:
            try:
                self.sock_handler.send_msg(data, d_type)
            except sock_handling.ConnectionError as error:
                pass
        else:
            pass

    #################################################################
    def on_double_click(self, event):  # need rewrite
        def tag():
            self.msg_box_entry.insert(END, "@%s " % name)
            self.msg_box_entry.focus_set()

        def poke():
            self.new_window = Toplevel(self.master)
            send_poke_window.SendPokeWindow(self.new_window, self, name)

        def p_chat():
            pass

        widget = event.widget
        selection = widget.curselection()
        name = widget.get(selection[0])
        print "selection:", selection, ": '%s'" % name

        menu = Menu(self.master, tearoff=0)
        if name != self.username:
            menu.add_command(label='Tag', command=tag)
            menu.add_command(label='Poke', command=poke)
            menu.add_command(label='Start private chat (&Voice)', command=p_chat)
        else:
            menu.add_command(label='Coming Soon')

        menu.post(event.x_root, event.y_root)
    #################################################################