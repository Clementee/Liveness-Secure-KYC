from tkinter import *


class SelectDevice:
    def __init__(self, parent, devices):
        """
        Initializes the Select device pop-up that spawns when we use the camera
        @param parent: The root Tk we use
        @param devices: The list of camera devices the computer has
        """
        self.device_id = None

        top = self.top = Toplevel(parent)
        top.attributes("-toolwindow", 1)
        top.attributes("-topmost", 1)
        top.geometry("250x200")
        top.resizable(False, False)
        top.columnconfigure(0, weight=1)
        top.rowconfigure(1, weight=1)

        self.myLabel = Label(top, text='Select a video device:')
        self.myLabel.grid(padx=5, pady=5)

        self.listbox = Listbox(top, selectmode=SINGLE)
        self.listbox.grid(sticky=W + E + N + S, padx=5, pady=5)
        for item in devices:
            self.listbox.insert(END, item)

        self.mySubmitButton = Button(top, text='Ok', width=10, command=self.send)
        self.mySubmitButton.grid(padx=5, pady=5)

        top.bind('<Return>', lambda event: self.send())

    def send(self):
        """
        Sends to the rest of the method through a lambda the device chosen for the camera
        """
        self.device_id = self.listbox.curselection()[0]
        self.top.destroy()
