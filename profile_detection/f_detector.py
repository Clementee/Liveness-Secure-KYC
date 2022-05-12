import cv2
import numpy as np

import config as cfg
import f_utils


def detect(img, cascade):
    """
    Detect the confidence score of finding such objects in the cascade
    :param img: The image to classify
    :param cascade: The HaarCascade model objects
    :return: The confidence score and the objects
    """
    rects, _, confidence = cascade.detectMultiScale3(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                                     flags=cv2.CASCADE_SCALE_IMAGE, outputRejectLevels=True)
    if len(rects) == 0:
        return (), ()
    rects[:, 2:] += rects[:, :2]
    return rects, confidence


def convert_rightbox(img, box_right):
    """
    Convert the coordinates of the boxes
    :param img: The image to work on
    :param box_right: All the boxes right
    :return: The boxes coordinates converted
    """
    res = np.array([])
    _, x_max = img.shape
    for box_ in box_right:
        box = np.copy(box_)
        box[0] = x_max - box_[2]
        box[2] = x_max - box_[0]
        if res.size == 0:
            res = np.expand_dims(box, axis=0)
        else:
            res = np.vstack((res, box))
    return res


class detect_face_orientation:
    def __init__(self):
        # Initialize the detector of frontal face shots
        self.detect_frontal_face = cv2.CascadeClassifier(cfg.detect_frontal_face)
        # Initialize the detector of profile face shots
        self.detect_profile_face = cv2.CascadeClassifier(cfg.detect_profile_face)

    def face_orientation(self, gray):
        """
        Return the face orientation from a shot
        :param gray: The gray image from which we need to detect the face orientation
        :return: The face orientation
        """
        # left_face
        box_left, w_left = detect(gray, self.detect_profile_face)
        if len(box_left) == 0:
            box_left = []
            name_left = []
        else:
            name_left = len(box_left) * ["left"]
        # right_face
        gray_flipped = cv2.flip(gray, 1)
        box_right, w_right = detect(gray_flipped, self.detect_profile_face)
        if len(box_right) == 0:
            box_right = []
            name_right = []
        else:
            box_right = convert_rightbox(gray, box_right)
            name_right = len(box_right) * ["right"]

        boxes = list(box_left) + list(box_right)
        names = list(name_left) + list(name_right)
        if len(boxes) == 0:
            return boxes, names
        else:
            index = np.argmax(f_utils.get_areas(boxes))
            boxes = [boxes[index].tolist()]
            names = [names[index]]
        return boxes, names
