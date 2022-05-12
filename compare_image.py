# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import re
import warnings

import face_recognition.api as face_recognition
import scipy.misc


def scan_known_people(known_people_folder):
    """
    :param known_people_folder: The folder/image in our case that will be used to be compared
    :return: Add the picture to the known names/face encodings pairs to compare the second picture to
    """
    known_names = []
    known_face_encodings = []

    basename = known_people_folder
    img = face_recognition.load_image_file(known_people_folder)
    encodings = face_recognition.face_encodings(img)
    if len(encodings) == 1:
        known_names.append(basename)
        known_face_encodings.append(encodings[0])
    return known_names, known_face_encodings


def test_image(image_to_check, known_names, known_face_encodings):
    """
    The test image we compare to the known names and face pairs that we used to initialize before
    :param image_to_check: The path to the image we want to compare it to
    :param known_names: The known names (here only using one name, the name of the other image to compare it to)
    :param known_face_encodings: The face associated to the known name
    :return: The distance between the two images and the result (either same person or not)
    """
    unknown_image = face_recognition.load_image_file(image_to_check)
    i = False
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
            print(distance[0])
            # print("True") if True in result else print("False ")
            if True in result:
                i = True
        return distance[0], i
    else:
        return "0", "Many Faces or No Faces"


def image_files_in_folder(folder):
    """
    Retrieve all the pictures from the folder given as input
    :param folder: The path to the folder we want to retrieve the pictures from
    :return: The picture files from the folder
    """
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


def compare_image(test1, test2):
    """
    The function that we call to compare the two and receive the results
    :return: The distance between the two pictures, and the result, whether the two pictures are related to the same person or not
    """
    known_names, known_face_encodings = scan_known_people(test1)
    distance, result = test_image(test2, known_names, known_face_encodings)
    return distance, result
