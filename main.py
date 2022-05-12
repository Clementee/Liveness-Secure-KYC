from gui.HomePageWindow import *

# Main page manager that handles the creation of the tkinter instance by calling Tk() and setting the homepage window as the active page
if __name__ == "__main__":

    os.remove("modified/A0.jpg") if os.path.exists("modified/A0.jpg") else None
    os.remove("modified/A1.jpg") if os.path.exists("modified/A1.jpg") else None
    os.remove("modified/A2.jpg") if os.path.exists("modified/A2.jpg") else None
    os.remove("images/card.jpg") if os.path.exists("images/card.jpg") else None
    os.remove("images/face.jpg") if os.path.exists("images/face.jpg") else None
    os.remove("images/selfie.png") if os.path.exists("images/selfie.png") else None
    root = Tk()
    my_gui = HomePageWindow(root)
    root.mainloop()
