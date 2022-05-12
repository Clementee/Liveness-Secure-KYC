import cv2
import numpy as np


def save_image(filename, img):
    cv2.imwrite(filename, img)


def sepia(img):
    kernel = np.float32([
        [0.272, 0.534, 0.131],
        [0.349, 0.686, 0.168],
        [0.393, 0.769, 0.189]])
    return cv2.transform(img, kernel)


def edge_preserving(img):
    return cv2.edgePreservingFilter(img)


def stylization(img):
    return cv2.stylization(img)


def pencil_sketch(img):
    _, res = cv2.pencilSketch(img)
    return res