import cv2
import dlib
import numpy as np
import f_utils
from blink_detection import f_blink_detection
from emotion_detection import f_emotion_detection
from profile_detection import f_detector

# Initialize all the detectors (front face, profile, emotion and blink detectors)
frontal_face_detector = dlib.get_frontal_face_detector()
profile_detector = f_detector.detect_face_orientation()
emotion_detector = f_emotion_detection.predict_emotions()
blink_detector = f_blink_detection.eye_blink_detector()


def detect_liveness(im, COUNTER=0, TOTAL=0):
    """
    Update properties
    :param im: The live feed image used to detect the liveness
    :param COUNTER: The counter used
    :param TOTAL: The total required
    :return: An array containing the updates for all the liveness properties checked
    """

    # Process the image in gray to compute the detection without worrying about colors
    gray = gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    # Detect the face and box the face to store the coordinates
    rectangles = frontal_face_detector(gray, 0)
    boxes_face = f_utils.convert_rectangles2array(rectangles, im)

    # If the number of faces detected is superior to 0
    if len(boxes_face) != 0:
        # We only keep the face detected with the largest area covered, thus keeping the main subject
        areas = f_utils.get_areas(boxes_face)
        index = np.argmax(areas)
        rectangles = rectangles[index]
        boxes_face = [list(boxes_face[index])]

        # -------------------------------------- emotion_detection ---------------------------------------
        '''
        Used to verify whether the user is happy/neutral/angry/suprised..
        
        input:
            - image RGB
            - boxes_face: [[579, 170, 693, 284]]
        output:
            - status: "ok"
            - emotion: ['happy'] or ['neutral'] ...
            - box: [[579, 170, 693, 284]]
        '''
        _, emotion = emotion_detector.get_emotion(im, boxes_face)

        # -------------------------------------- blink_detection ---------------------------------------
        '''
        Use to verify the user has blinked
        
        input:
            - image gray
            - rectangles
        output:
            - status: "ok"
            - COUNTER: number of consecutive frames under the threshold
            - TOTAL: number of blinks
        '''
        COUNTER, TOTAL = blink_detector.eye_blink(gray, rectangles, COUNTER, TOTAL)
    else:
        boxes_face = []
        emotion = []
        TOTAL = 0
        COUNTER = 0

    # -------------------------------------- profile_detection ---------------------------------------
    '''
    Used for the turn your face left/right to verify the face has been rotated to the profile
    
    input:
        - image gray
    output:
        - status: "ok"
        - profile: ["right"] or ["left"]
        - box: [[579, 170, 693, 284]]
    '''
    box_orientation, orientation = profile_detector.face_orientation(gray)

    # -------------------------------------- output ---------------------------------------
    output = {
        'box_face_frontal': boxes_face,
        'box_orientation': box_orientation,
        'emotion': emotion,
        'orientation': orientation,
        'total_blinks': TOTAL,
        'count_blinks_consecutives': COUNTER
    }
    return output
