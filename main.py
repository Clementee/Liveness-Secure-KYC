from gui.HomePageWindow import *

# Main page manager that handles the creation of the tkinter instance by calling Tk() and setting the homepage window as the active page
if __name__ == "__main__":
    root = Tk()
    my_gui = HomePageWindow(root)
    root.mainloop()
