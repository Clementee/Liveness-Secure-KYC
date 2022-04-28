import queue
from tkinter import messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from gui.SelectDevice import *
from gui.ConfigureRecording import *
from pygrabber.PyGrabber import *
from gui.image_process import *


class MainWindow:

    def __init__(self, master):
        """
        @param self:
        @param master:
        """
        self.change_camera_btn = None
        self.lbl_status1 = None
        self.save_btn = None
        self.master = None
        self.grab_btn = None
        self.canvas = None
        self.plot = None
        self.image_controls_area2 = None
        self.image_controls_area = None
        self.image_area = None
        self.status_area = None
        self.video_area = None
        self.create_gui(master)
        self.grabber = PyGrabber(self.on_image_received)
        self.queue = queue.Queue()
        self.image = None
        self.original_image = None
        self.select_device()

    def create_gui(self, master):
        """
        @param self: The main window on which we apply the creation
        @param master:
        """
        self.master = master
        master.title("Python Photo App")

        master.columnconfigure(0, weight=1, uniform="group1")
        master.columnconfigure(1, weight=1, uniform="group1")
        master.rowconfigure(0, weight=1)

        self.video_area = Frame(master, bg='black')
        self.video_area.grid(row=0, column=0, sticky=W + E + N + S, padx=5, pady=5)

        self.status_area = Frame(master)
        self.status_area.grid(row=1, column=0, sticky=W + E + N + S, padx=5, pady=5)

        self.image_area = Frame(master)
        self.image_area.grid(row=0, column=1, sticky=W + E + N + S, padx=5, pady=5)

        self.image_controls_area = Frame(master)
        self.image_controls_area.grid(row=1, column=1, padx=5, pady=0)

        # Grabbed image
        fig = Figure(figsize=(5, 4), dpi=100)
        self.plot = fig.add_subplot(111)
        self.plot.axis('off')

        self.canvas = FigureCanvasTkAgg(fig, master=self.image_area)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=1)

        # Status
        self.lbl_status1 = Label(self.status_area, text="No device selected")
        self.lbl_status1.grid(row=0, column=0, padx=5, pady=5, sticky=W)

        # Image controls
        self.grab_btn = Button(self.image_controls_area, text="Grab", command=self.grab_frame)
        self.grab_btn.pack(padx=5, pady=20, side=LEFT)

        self.save_btn = Button(self.image_controls_area, text="Save", command=self.save_image)
        self.save_btn.pack(padx=5, pady=2, side=RIGHT)

        self.change_camera_btn = Button(self.image_controls_area, text="Change Camera", command=self.change_camera)
        self.change_camera_btn.pack(padx=5, pady=2, side=RIGHT)

        self.video_area.bind("<Configure>", self.on_resize)

    def display_image(self):
        while self.queue.qsize():
            try:
                self.image = self.queue.get()
                self.original_image = self.image
                self.plot.imshow(np.flip(self.image, axis=2))
                self.canvas.draw()
            except queue.Empty:
                pass
        self.master.after(100, self.display_image)

    def select_device(self):
        input_dialog = SelectDevice(self.master, self.grabber.get_video_devices())
        self.master.wait_window(input_dialog.top)
        # no device selected
        if input_dialog.device_id is None:
            exit()

        self.grabber.set_device(input_dialog.device_id)
        self.grabber.start_preview(self.video_area.winfo_id())
        self.display_status(self.grabber.get_status())
        self.on_resize(None)
        self.display_image()

    def display_status(self, status):
        self.lbl_status1.config(text=status)

    def change_camera(self):
        self.grabber.stop()
        del self.grabber
        self.grabber = PyGrabber(self.on_image_received)
        self.select_device()

    def camera_properties(self):
        self.grabber.set_device_properties()

    def set_format(self):
        self.grabber.display_format_dialog()

    def on_resize(self, event):
        self.grabber.update_window(self.video_area.winfo_width(), self.video_area.winfo_height())

    def grab_frame(self):
        self.grabber.grab_frame()

    def on_image_received(self, image):
        self.queue.put(image)

    def save_image(self):
        filename = filedialog.asksaveasfilename(
            initialdir="/",
            title="Select file",
            filetypes=[('PNG', ".png"), ('JPG', ".jpg")])
        if filename is not None:
            save_image(filename, self.image)
