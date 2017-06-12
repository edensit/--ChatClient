from GUI import login_window
import sys

from Tkinter import *


def main():
    reload(sys)
    sys.setdefaultencoding('utf8')

    master = Tk()
    login_window.LoginWindow(master)
    master.iconbitmap('GFX\icon.ico')
    master.mainloop()

if __name__ == '__main__':
    main()

# CR extract magic numbers to constants and enums Make the code more modular - divide into files, classes, functions.
# http://www.makinggoodsoftware.com/2009/06/04/10-commandments-for-creating-good-code/
