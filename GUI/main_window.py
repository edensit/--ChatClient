import Queue
import cPickle
import thread
import tkMessageBox
from Tkinter import *
from tkFileDialog import askdirectory
import ttk
from datetime import datetime
from GUI import send_poke_window
from GUI import admin_ban_window
from socks import sock_handling, alert_audio_handling


class SoundPathEnum:
    MESSAGE = "sound/incoming_message.wav"
    BANNED = "sound/user_banned.wav"
    KICKED = "sound/user_kicked.wav"
    POKED = "sound/you_were_poked.wav"


class SendTypeEnum:
    TYPE_LOGIN = 1
    TYPE_REGISTER = 2
    TYPE_MSG = 3
    TYPE_COMMAND = 4
    TYPE_POKE = 5


class ReceiveTypeEnum:
    TYPE_MSG = 1
    TYPE_USER_LIST = 2
    TYPE_POKE = 3
    TYPE_CONNECTION_ERROR = 4


class MainWindow:
    def __init__(self, master, username, sock):
        self.master = master
        self.username = username

        self.sock_handler = sock_handling.SocketHandler(sock)
        self.master.iconbitmap('GFX\icon.ico')
        self.master.title("eChat Chat Client v1.0")
        self.master.geometry("775x395")
        self.master.resizable(width=False, height=False)

        self.master.protocol("WM_DELETE_WINDOW", self.window_close_handler)

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
        self.chat_textbox = Text(self.chat_frame, width=53, height=15, font=("Helvetica", 12))
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

        self.master.bind("<KeyRelease-Return>", lambda e: self.send_msg(self.msg_input.get()))

        self.send_button_frame = LabelFrame(self.master, text="", padx=6, pady=6.4)
        self.send_button_frame.grid(row=20, column=18, sticky=W + S)
        self.send_button = ttk.Button(
            self.send_button_frame, text='Send', command=lambda: self.send_msg(self.msg_input.get()), width=6)
        self.send_button.pack(fill=BOTH, expand=1)

        self.q = Queue.Queue()
        self.master.after(100, self.check_queue)
        thread.start_new_thread(self.received_messages, ())

        self.menu_bar = Menu(self.master)

        self.filemenu = Menu(self.menu_bar, tearoff=0)
        self.filemenu.add_command(label="Toggle Sound", command=self.toggle_sound)
        self.filemenu.add_command(label="Toggle Poke popup", command=self.toggle_poke_popup)
        self.filemenu.add_command(label="Save chat to txt file", command=self.save_chat_log)
        self.filemenu.add_command(label="ban list", command=self.admin_ban_window_handler)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.window_close_handler)
        self.menu_bar.add_cascade(label="eChat", menu=self.filemenu)

        self.helpmenu = Menu(self.menu_bar, tearoff=0)
        self.helpmenu.add_command(label="Help", command=self.donothing)
        self.helpmenu.add_command(label="About...", command=self.donothing)
        self.menu_bar.add_cascade(label="Help", menu=self.helpmenu)

        self.master.config(menu=self.menu_bar)

        self.sound_activate = True
        self.poke_popup_activate = True

        self.insert_local_msg("Connected to server! :)")

    def toggle_sound(self):
        if self.sound_activate:
            self.sound_activate = False
            self.insert_local_msg("Sound is now disabled", "RED")
        else:
            self.sound_activate = True
            self.insert_local_msg("Sound is now enabled", "RED")

    def toggle_poke_popup(self):
        if self.poke_popup_activate:
            self.poke_popup_activate = False
            self.insert_local_msg("Poke popup is now disabled", "RED")
        else:
            self.poke_popup_activate = True
            self.insert_local_msg("Poke popup is now enabled", "RED")

    def save_chat_log(self):
        directory_path = askdirectory()
        text = self.chat_textbox.get("1.0", 'end-1c')
        try:
            with open(directory_path + "/ChatLog.txt", "a") as outf:
                outf.write(text)
        except (IOError, OSError):
            self.insert_local_msg("Error: Save Failed", "RED")
        else:
            self.insert_local_msg("Log file successfully saved!", "RED")

    def donothing(self):
        pass

    def window_close_handler(self):
        if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
            self.sock_handler.close_socket()
            self.master.destroy()
            raise SystemExit

    def raw_data_handler(self, data):
        d_type = data[0]
        data = data[1]

        if d_type == ReceiveTypeEnum.TYPE_MSG:
            self.insert_msg(data)
        elif d_type == ReceiveTypeEnum.TYPE_USER_LIST:
            self.update_users_list(data)
        elif d_type == ReceiveTypeEnum.TYPE_POKE:
            self.incoming_poke_handler(data)
        elif d_type == ReceiveTypeEnum.TYPE_CONNECTION_ERROR:
            self.connection_error()

    def received_messages(self):
        while True:
            try:
                data = self.sock_handler.get_next_message()
            except sock_handling.EmptyMessagesQError:
                pass
            else:
                self.raw_data_handler(data)

    def check_queue(self): # Poke Queue
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
        self.insert_local_msg("%s - %s pokes you: %s\n" % (datetime.now().strftime('%H:%M:%S'), username, msg))

        if self.poke_popup_activate:
            tkMessageBox.showinfo("You Have Been Poked", "%s - %s pokes you: %s"
                                  % (datetime.now().strftime('%H:%M:%S'), username, msg))

    def insert_msg(self, data):  # d_type 1 - msg
        self.insert_local_msg("<%s> %s\n" % (datetime.now().strftime('%H:%M:%S'), data))
        self.chat_textbox.see(END)
        if self.sound_activate:
            alert_audio_handling.play_sound(SoundPathEnum.MESSAGE)

    def insert_local_msg(self, msg, color="BLACK"):
        self.chat_textbox.insert(END, "%s\n" % msg, color)
        self.chat_textbox.see(END)

    def update_users_list(self, data):  # d_type 2 - users list
        self.user_list.delete(0, END)
        users_list = cPickle.loads(data)
        for user in users_list:
            self.user_list.insert(END, user)

    def incoming_poke_handler(self, data):  # d_type 3 - poke
        self.q.put(lambda: self.show_poke(data))

    def admin_ban_window_handler(self):  # d_type 3 - poke
        admin_ban_window.AdminBanWindow(self)

    def connection_error(self):
        self.insert_local_msg("Connection to server lost!", "RED")
        self.chat_textbox.see(END)

    def send_msg(self, data, d_type=SendTypeEnum.TYPE_MSG, arg=0):
        data = str(data)
        if len(data) >= 1 and d_type == SendTypeEnum.TYPE_MSG:
            try:
                self.insert_local_msg('<%s> [Me] %s' % (datetime.now().strftime('%H:%M:%S'), data))
                self.sock_handler.send_msg(data)
            except sock_handling.ConnectionError:
                self.insert_local_msg("Error: Connection to server lost! The message was not delivered", "RED")
            else:
                pass
            finally:
                self.msg_box_entry.delete(0, 'end')
                self.chat_textbox.see(END)
                self.msg_box_entry.focus_set()
        elif d_type != SendTypeEnum.TYPE_MSG:
            try:
                self.sock_handler.send_msg(data, d_type)
            except sock_handling.ConnectionError:
                pass
        else:
            pass

    #################################################################
    def on_double_click(self, event):  # need rewrite
        def tag():
            self.msg_box_entry.insert(END, "@%s " % name)
            self.msg_box_entry.focus_set()

        def poke():
            send_poke_window.SendPokeWindow(self, name)

        def kick():
            self.msg_box_entry.insert(END, "!kick %s " % name)
            self.msg_box_entry.focus_set()

        widget = event.widget
        selection = widget.curselection()
        name = widget.get(selection[0])
        print "selection:", selection, ": '%s'" % name

        if "[Admin]" in name:
            name = name[7:]

        menu = Menu(self.master, tearoff=0)
        if name.lower() != self.username.lower():
            menu.add_command(label='Tag', command=tag)
            menu.add_command(label='Poke', command=poke)
            menu.add_command(label='kick', command=kick)
        else:
            menu.add_command(label='Coming Soon')

        menu.post(event.x_root, event.y_root)
    #################################################################
