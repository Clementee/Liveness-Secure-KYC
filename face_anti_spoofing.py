import random
import cv2
import imutils
import f_liveness_detection
import questions

# instanciar camara
from gui.MainWindow import *

cv2.namedWindow('liveness_detection')
cam = cv2.VideoCapture('http://128.179.130.18:4747/mjpegfeed')

# parameters 
COUNTER, TOTAL = 0, 0
counter_ok_questions = 0
counter_ok_consecutives = 0
limit_consecutives = 2
limit_questions = 2
counter_try = 0
limit_try = 120


def show_image(camera, text, color=(0, 0, 255)):
    ret_in, image = camera.read()
    image = imutils.resize(image, width=720)
    # im = cv2.flip(im, 1)
    cv2.putText(image, text, (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)
    return image


def show_image2(camera, text, text2, color=(0, 0, 255)):
    ret_in, image = camera.read()
    image = imutils.resize(image, width=720)
    # im = cv2.flip(im, 1)
    cv2.putText(image, text, (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)
    cv2.putText(image, text2, (10, 200), cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)
    return image


for i_questions in range(0, limit_questions):
    # genero aleatoriamente pregunta
    index_question = random.randint(0, 5)
    question = questions.question_bank(index_question)

    im = show_image(cam, question)
    cv2.imshow('liveness_detection', im)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    for i_try in range(limit_try):
        # <----------------------- ingestar data 
        ret, im = cam.read()
        im = imutils.resize(im, width=720)
        im = cv2.flip(im, 1)
        # <----------------------- ingestar data 
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
            img = show_image(cam, "", color=(0, 0, 0))
            cv2.imwrite('images/selfie.png', img)
            im = show_image2(cam, "LIFENESS SUCCESSFUL", "Press q to go next", color=(0, 255, 0))
            cv2.imshow('liveness_detection', im)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyWindow('liveness_detection')
                root = Tk()
                my_gui = MainWindow(root)
                root.mainloop()
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
