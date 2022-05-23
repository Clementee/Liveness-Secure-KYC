from __future__ import print_function

import queue
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from compare_image import compare_image
from gui.SelectDevice import *
from pygrabber.PyGrabber import *
import cv2

CASCADE = "Face_cascade.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE)


class MainWindow:
    def __init__(self, master):
        """
        Initialize the Tk instance by setting all GUI elements to Null and calling methods
        @param master: The Tk instance on which we work
        """
        self.save_btn = None
        self.image_filter_4_btn = None
        self.image_filter_3_btn = None
        self.grab_btn = None
        self.lbl_status1 = None
        self.canvas = None
        self.plot = None
        self.image_controls_area2 = None
        self.image_controls_area = None
        self.image_area = None
        self.status_area = None
        self.video_area = None
        self.master = None
        self.card = 0
        self.selfie = 0
        self.i = 0
        self.create_gui(master)
        self.grabber = PyGrabber(self.on_image_received)
        self.queue = queue.Queue()
        self.image = None
        self.original_image = None
        self.select_device()

    def create_gui(self, master):
        """
        Actually does the GUI implementation
        @param master: Again the Tk instance
        """
        self.master = master
        master.title("KYC Application")
        self.create_menu(master)

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

        self.image_controls_area2 = Frame(master)
        self.image_controls_area2.grid(row=2, column=1, padx=5, pady=0)

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

        self.image_filter_3_btn = Button(self.image_controls_area, text="Next",
                                         command=self.next)
        self.image_filter_3_btn.pack(padx=5, pady=2, side=LEFT)

        self.image_filter_4_btn = Button(self.image_controls_area2, text="Save Selfie",
                                         command=self.save_image2)
        self.image_filter_4_btn.pack(padx=5, pady=2, side=LEFT)

        self.save_btn = Button(self.image_controls_area2, text="Save ID Card picture", command=self.save_image)
        self.save_btn.pack(padx=5, pady=2, side=LEFT)

        self.video_area.bind("<Configure>", self.on_resize)

    def create_menu(self, master):
        """
        Create a rolling, cascade menu with choices
        @param master: The Tk instance
        """
        menubar = Menu(master)
        self.master.config(menu=menubar)
        image_menu = Menu(menubar)
        image_menu.add_command(label="Grab image", command=self.grab_frame)
        image_menu.add_command(label="Save...", command=self.save_image)
        menubar.add_cascade(label="Image", menu=image_menu)

    def display_image(self):
        """
        Display the image we have
        """
        while self.queue.qsize():
            try:
                self.image = self.queue.get(0)
                self.original_image = self.image
                self.plot.imshow(np.flip(self.image, axis=2))
                self.canvas.draw()
            except queue.Empty:
                pass
        self.master.after(100, self.display_image)

    def select_device(self):
        """
        Manage the selection of the device for the camera
        """
        input_dialog = SelectDevice(self.master, self.grabber.get_video_devices())
        self.master.wait_window(input_dialog.top)
        # no device selected
        if input_dialog.device_id is None:
            exit()

        self.grabber.set_device(input_dialog.device_id)
        self.grabber.start_preview(self.video_area.winfo_id())
        self.display_status(self.grabber.get_status())
        self.on_resize()
        self.display_image()

    def display_status(self, status):
        """
        @param status: Edit the status text from the Tk instance
        """
        self.lbl_status1.config(text=status)

    def on_resize(self):
        """
        Manage the update of the window depending on the size of the video
        """
        self.grabber.update_window(self.video_area.winfo_width(), self.video_area.winfo_height())

    def init_device(self):
        """
        Initialize the grabber for the device selection
        """
        self.grabber.start()

    def grab_frame(self):
        """
        Grab the frame from the image grabber
        """
        self.grabber.grab_frame()

    def on_image_received(self, image):
        """
        @param image: Put the image in the queue that we received
        """
        self.queue.put(image)

    def stop(self):
        """
        Stop the grabber
        """
        self.grabber.stop()
        self.display_status(self.grabber.get_status())

    def save_image(self):
        """
        Save the image for the ID card
        """
        self.card = 1
        cv2.imwrite('images/card.jpg', self.image)

    def save_image2(self):
        """
        Save the image for the selfie
        """
        self.selfie = 1
        cv2.imwrite('images/face.jpg', self.image)

    def next(self):
        """
        What to do after we imported all the pictures
        """
        if self.card == 0:
            self.display_status("Take picture of ID Card")
            print("Take picture of ID card")
        elif self.selfie == 0:
            self.display_status("Take selfie (picture of yourself)")
            print("Take selfie (picture of yourself)")
        else:
            # For all the images in the folder (meaning the ones that we just took), we only take the face
            for image in os.listdir("images"):
                try:
                    print("Processing.....", os.path.abspath(os.path.join("images", image)))
                    self.detect_faces(os.path.abspath(os.path.join("images", image)), False)
                    self.i += 1
                except Exception:
                    print("Could not process ", os.path.abspath(os.path.join("images", image)))
            # Compare the ID card picture with the Selfie's one, if its the same then r1 == True
            _, r1 = compare_image("modified/A1.jpg", "modified/A2.jpg")
            # Same for the comparison between the selfie and the random shot, if same r2 == True
            _, r2 = compare_image("modified/A0.jpg", "modified/A1.jpg")
            if r1 & r2:
                # If both are True, the KYC worked perfectly fine
                print("True")
                self.master.destroy()
            elif r1 == True & r2 == False:
                # If r2 is false then the ID card and the selfie don't correspond
                print("The ID card and the selfie are not the same person")
                self.master.destroy()
            elif r1 == False & r2 == True:
                # If r1 is false then the selfie and the random shot from the liveness check don't correspond
                print("The KYC check and selfie are not the same person, stop cheating")
                self.master.destroy()
            else:
                # Both are false => the shots don't match in any form
                print("Everything is wrong")
                self.master.destroy()

    def detect_faces(self, image_path, display=True):
        """
        Extract the faces from all the pictures in the given folder
        @param image_path:  The path to the folder from which we want to extract the faces
        """
        image = cv2.imread(image_path)
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = FACE_CASCADE.detectMultiScale(image_grey, scaleFactor=1.16, minNeighbors=5, minSize=(25, 25), flags=0)

        for x, y, w, h in faces:
            sub_img = image[y - 10:y + h + 10, x - 10:x + w + 10]
            os.chdir("modified")
            cv2.imwrite("A" + str(self.i) + ".jpg", sub_img)
            os.chdir("../")
            # cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)

        if display:
            cv2.imshow("Faces Found", image)
