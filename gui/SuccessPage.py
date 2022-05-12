from PIL import ImageTk

from gui.MainWindow import *


class SuccessPage:

    master = None

    def __init__(self, master):
        """
        @param self:
        @param master:
        """
        self.master = None
        master.columnconfigure(index=0, weight=1)
        master.columnconfigure(index=1, weight=2)
        master.rowconfigure(index=0, weight=1)
        master.rowconfigure(index=1, weight=10)
        master.rowconfigure(index=3, weight=1)
        self.create_gui(master)

    def change_window(self):
        self.master.destroy()

    def create_gui(self, master):
        """
        @param self: The main window on which we apply the creation
        @param master:
        """
        self.master = master
        w, h = master.winfo_screenwidth() - 200, master.winfo_screenheight() - 200
        master.configure(background="black")
        master.geometry("%dx%d" % (800, h))
        master.title("KYC Application")
        mainText = Label(master, text="KYC Application", fg="white", bg="black")
        mainText.config(font=("Product Sans", 44))
        mainText.grid(row=0, column=0)
        img = ImageTk.PhotoImage(file="visuals/KYC.jpg")
        firstImg = Label(master, image=img, borderwidth=0)
        master.photo = img
        firstImg.grid(row=1, column=0)
        btn = Button(master, text="Congratulations", bd='2', command=self.change_window)
        btn.grid(row=3, column=0)

