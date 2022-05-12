from PIL import ImageTk
from gui.MainWindow import *


# Home Page Window manager
class HomePageWindow:

    def __init__(self, master):
        """
        Initialization of the GUI for the Tkinter instance, configuring the rows and columns
        @param self: default parameter
        @param master: the Tk instance we work on
        """
        self.master = None
        master.columnconfigure(index=0, weight=1)
        master.columnconfigure(index=1, weight=2)
        master.rowconfigure(index=0, weight=1)
        master.rowconfigure(index=1, weight=10)
        master.rowconfigure(index=3, weight=1)
        self.create_gui(master)

    def change_window(self):
        """
        This function manages the switch of window when calling the button, destroying the previous Tk instance and
        calling the liveness detection snippet of code
        """
        self.master.destroy()
        os.system('python face_anti_spoofing.py')

    def create_gui(self, master):
        """
        Managing the GUI by configuring the background + the size of the application ° the title and the different
        components
        @param master: The tk instance we work on
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
        btn = Button(master, text="Launch process", bd='2', command=self.change_window)
        btn.grid(row=3, column=0)
