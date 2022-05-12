#
# python_grabber
#
# Authors:
#  Andrea Schiavinato <andrea.schiavinato84@gmail.com>
#
# Copyright (C) 2019 Andrea Schiavinato
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NON INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
from __future__ import print_function

from compare_image import compare_image
from gui.FailurePage import *
from gui.SuccessPage import *

import queue
from tkinter import messagebox

import os
import re
import scipy.misc
import warnings
import face_recognition.api as face_recognition
import sys

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui.ConfigureRecording import *
from gui.SelectDevice import *
from gui.image_process import *
from pygrabber.PyGrabber import *

CASCADE = "Face_cascade.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE)


class MainWindow:
    def __init__(self, master):
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
        menubar = Menu(master)
        self.master.config(menu=menubar)

        camera_menu = Menu(menubar)
        camera_menu.add_command(label="Open...", command=self.change_camera)
        camera_menu.add_command(label="Set properties...", command=self.camera_properties)
        camera_menu.add_command(label="Set format...", command=self.set_format)
        camera_menu.add_command(label="Start preview", command=self.start_preview)
        camera_menu.add_command(label="Stop", command=self.stop)
        menubar.add_cascade(label="Camera", menu=camera_menu)

        image_menu = Menu(menubar)
        image_menu.add_command(label="Grab image", command=self.grab_frame)
        image_menu.add_command(label="Save...", command=self.save_image)
        menubar.add_cascade(label="Image", menu=image_menu)

    def display_image(self):
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

    def on_resize(self):
        self.grabber.update_window(self.video_area.winfo_width(), self.video_area.winfo_height())

    def init_device(self):
        self.grabber.start()

    def grab_frame(self):
        self.grabber.grab_frame()

    def start_stop_recording(self):
        audio_devices = self.grabber.get_audio_devices()
        video_compressors = self.grabber.get_video_compressors()
        audio_compressors = self.grabber.get_audio_compressors()
        asf_profiles = self.grabber.get_asf_profiles()
        input_dialog = ConfigureRecording(self.master, audio_devices, video_compressors, audio_compressors,
                                          asf_profiles)
        self.master.wait_window(input_dialog.top)
        if input_dialog.result:
            try:
                self.grabber.start_recording(input_dialog.get_audio_device_index(),
                                             input_dialog.get_video_compressor_index(),
                                             input_dialog.get_audio_compressor_index(),
                                             input_dialog.get_filename(),
                                             self.video_area.winfo_id())
                self.grabber.update_window(self.video_area.winfo_width(), self.video_area.winfo_height())
                self.display_status(self.grabber.get_status())
            except:
                messagebox.showinfo("Error",
                                    "An error occurred during the recoding. Select a different comnination of compressors and try again.")
                self.display_status(self.grabber.get_status())

    def on_image_received(self, image):
        self.queue.put(image)

    def start_preview(self):
        self.grabber.start_preview(self.video_area.winfo_id())
        self.display_status(self.grabber.get_status())
        self.on_resize()

    def stop(self):
        self.grabber.stop()
        self.display_status(self.grabber.get_status())

    def save_image(self):
        self.card = 1
        cv2.imwrite('images/card.jpg', self.image)

    def save_image2(self):
        self.selfie = 1
        cv2.imwrite('images/face.jpg', self.image)

    # filename = filedialog.asksaveasfilename(
    #  initialdir="/",
    # title="Select file",
    # filetypes=[('PNG', ".png"), ('JPG', ".jpg")])
    # if filename is not None:
    #   save_image(filename, self.image)

    def image_filter(self, process_function):
        def inner():
            if self.original_image is None:
                return
            self.image = process_function(self.original_image)
            self.plot.imshow(np.flip(self.image, axis=2))
            self.canvas.draw()

        return inner

    def next(self):
        if self.card == 0:
            print("Take picture of ID card")
        elif self.selfie == 0:
            print("Take picture of selfie (yourself)")
        else:
            for image in os.listdir("images"):
                try:
                    print("Processing.....", os.path.abspath(os.path.join("images", image)))
                    self.detect_faces(os.path.abspath(os.path.join("images", image)), False)
                    self.i += 1
                except Exception:
                    print("Could not process ", os.path.abspath(os.path.join("images", image)))
            compare_image(self)
            known_names, known_face_encodings = self.scan_known_people()
            distance, result = self.test_image(known_names, known_face_encodings)
            # do the computation

    def detect_faces(self, image_path, display=True):
        image = cv2.imread(image_path)
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = FACE_CASCADE.detectMultiScale(image_grey, scaleFactor=1.16, minNeighbors=5, minSize=(25, 25), flags=0)

        for x, y, w, h in faces:
            sub_img = image[y - 10:y + h + 10, x - 10:x + w + 10]
            os.chdir("modified")
            cv2.imwrite("A" + str(self.i) + ".jpg", sub_img)
            os.chdir("../")
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)

        if display:
            cv2.imshow("Faces Found", image)

    def restore_original_image(self):
        if self.original_image is None:
            return
        self.image = self.original_image
        self.plot.imshow(np.flip(self.image, axis=2))
        self.canvas.draw()

    def scan_known_people(self):
        known_names = []
        known_face_encodings = []

        basename = "modified/A0.jpg"
        img = face_recognition.load_image_file("modified/A0.jpg")
        encodings = face_recognition.face_encodings(img)
        if len(encodings) == 1:
            known_names.append(basename)
            known_face_encodings.append(encodings[0])
        return known_names, known_face_encodings

    def test_image(self, known_names, known_face_encodings):
        unknown_image = face_recognition.load_image_file("modified/A1.jpg")

        # Scale down image if it's giant so things run a little faster
        if unknown_image.shape[1] > 1600:
            scale_factor = 1600.0 / unknown_image.shape[1]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                unknown_image = scipy.misc.imresize(unknown_image, scale_factor)

        unknown_encodings = face_recognition.face_encodings(unknown_image)
        if len(unknown_encodings) == 1:
            for unknown_encoding in unknown_encodings:
                result = face_recognition.compare_faces(known_face_encodings, unknown_encoding)
                distance = face_recognition.face_distance(known_face_encodings, unknown_encoding)

                if True in result:
                    f = open("text.txt", "r")
                    txt = f.read()
                    if txt == "True":
                        print(distance[0])
                        print("True")
                        self.master.destroy()
                        root = Tk()
                        my_gui = SuccessPage(root)
                        root.mainloop()
                    else:
                        print("The KYC check and selfie are not the same person, stop cheating")
                        self.master.destroy()
                        root = Tk()
                        my_gui = FailurePage(root)
                        root.mainloop()
                else:
                    print(distance[0])
                    print("The ID card and the selfie are not the same person")
                    self.master.destroy()

            return distance[0], result[0]
        else:
            return "0", "Many Faces or No Faces"

    def image_files_in_folder(folder):
        return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

