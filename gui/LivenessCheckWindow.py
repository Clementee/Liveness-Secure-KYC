from time import *

import PIL.Image
import PIL.ImageTk
import cv2
from PIL import ImageTk
import imutils
import f_liveness_detection
import questions
import random
import cv2

from gui.SelectDevice import *


def show_image(cam, text, color=(0, 0, 255)):
    ret, im = cam.read()
    im = imutils.resize(im, width=720)
    # im = cv2.flip(im, 1)
    cv2.putText(im, text, (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)
    return im


class LivenessCheckWindow:

    def __init__(self, master):
        """
        @param self:
        @param master:
        """
        self.delay = None
        self.photo = None
        self.btn_snapshot = None
        self.canvas = None
        self.vid = None
        self.video_source = None
        self.master = None
        self.create_gui(master)

    def create_gui(self, master):
        """
        @param self: The main window on which we apply the creation
        @param master:
        """

        # parameters
        COUNTER, TOTAL = 0, 0
        counter_ok_questions = 0
        counter_ok_consecutives = 0
        limit_consecutives = 3
        limit_questions = 3
        counter_try = 0
        limit_try = 500

        self.master = master
        master.title("Liveness Detection Recording")
        w, h = master.winfo_screenwidth() - 200, master.winfo_screenheight() - 200
        master.configure(background="black")
        master.geometry("%dx%d" % (800, h))
        self.video_source = 'http://128.179.133.122:4747/mjpegfeed'
        # self.vid = MyVideoCapture(self.video_source, master)

        cam = cv2.VideoCapture(self.video_source)

        # to edit everytime
        # self.canvas = Canvas(master, width=800, height=h)
        # self.canvas.pack(anchor=N, expand=True)

        # self.btn_snapshot = Button(master, text="Snapshot", width=50, command=self.snapshot)
        # self.btn_snapshot.pack(anchor=CENTER, expand=True)

        for i_questions in range(0, limit_questions):

            index_question = random.randint(0, 5)
            question = questions.question_bank(index_question)

            im = show_image(cam, question)
            imgtk = ImageTk.PhotoImage(image=im)
            cv2.imshow('liveness_detection', im)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            for i_try in range(limit_try):
                ret, im = cam.read()
                im = imutils.resize(im, width=720)
                im = cv2.flip(im, 1)
                TOTAL_0 = TOTAL
                out_model = f_liveness_detection.detect_liveness(im, COUNTER, TOTAL_0)
                TOTAL = out_model['total_blinks']
                COUNTER = out_model['count_blinks_consecutives']
                dif_blink = TOTAL - TOTAL_0
                if dif_blink > 0:
                    blinks_up = 1
                else:
                    blinks_up = 0

                challenge_res = questions.challenge_result(question, out_model, blinks_up)

                im = show_image(cam, question)
                cv2.imshow('liveness_detection', im)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                if challenge_res == "pass":
                    im = show_image(cam, question + " : ok")
                    cv2.imshow('liveness_detection', im)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                    counter_ok_consecutives += 1
                    if counter_ok_consecutives == limit_consecutives:
                        counter_ok_questions += 1
                        counter_try = 0
                        counter_ok_consecutives = 0
                        break
                    else:
                        continue

                elif challenge_res == "fail":
                    counter_try += 1
                    show_image(cam, question + " : fail")
                elif i_try == limit_try - 1:
                    break

            if counter_ok_questions == limit_questions:
                while True:
                    im = show_image(cam, "LIFENESS SUCCESSFUL", color=(0, 255, 0))
                    cv2.imshow('liveness_detection', im)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            elif i_try == limit_try - 1:
                while True:
                    im = show_image(cam, "LIFENESS FAIL")
                    cv2.imshow('liveness_detection', im)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                break

            else:
                continue
        self.master.mainloop()

    def update(self):
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)

    def snapshot(self):
        ret, frame = self.vid.get_frame()
        if ret:
            cv2.imwrite("frame-" + strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        self.master.after(self.delay, self.update)


class MyVideoCapture:
    def __init__(self, video_source, master):
        self.master = master
        if video_source is None:
            video_source = 0
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.width, self.height = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

    def show_frame(self):
        _, frame = self.vid.read()
        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = PIL.Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.master.imgtk = imgtk
        self.master.configure(image=imgtk)
        self.master.after(10, self.show_frame)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return ret, None
        else:
            return None, None
