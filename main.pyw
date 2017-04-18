from GUI import login_window
import sys

from Tkinter import *


def main():
    reload(sys)
    sys.setdefaultencoding('utf8')

    master = Tk()
    login_window.LoginWindow(master)
    master.mainloop()

if __name__ == '__main__':
    main()
