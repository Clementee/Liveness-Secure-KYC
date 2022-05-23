import random
import imutils
import f_liveness_detection
import questions
from gui.MainWindow import *
import cv2
import numpy as np

# Since my webcam doesn't work on my computer, I have to use DroidCam and change every time depending on the IP address of my phone
vid_address = "128.179.131.53:4747"

# Initialize the new window, this time using Open-CV to manage the display
cv2.namedWindow('KYC Application')
cam = cv2.VideoCapture('http://' + vid_address + '/mjpegfeed')

# Parameters used for the Liveness check
COUNTER, TOTAL = 0, 0
counter_ok_questions = 0
counter_ok_consecutive = 0
limit_consecutive = 2
limit_questions = 3
counter_try = 0
limit_try = 120


def display_im(camera, text, index, status, color=(0, 0, 255)):
    """
    The function takes the camera feed resized and with added text
    :param camera: The video feed captured from the camera, using Open-CV
    :param text: Used to display text on the image to give the questions
    :param color: Color of the text to display
    :param status: Status (either fail/running or valid)
    :param index: Index of the question currently answered/displayed

    :return: Return the feed from the camera resized with the text displayed
    """

    ret_in, image = camera.read()
    # Resize the shot
    image = imutils.resize(image, width=1500)

    foreground = "visuals/"
    if index == 0:
        foreground = foreground + "smile"
        text = "Smile"
    elif index == 1:
        foreground = foreground + "surprise"
        text = "Surprise face"
    elif index == 2:
        foreground = foreground + "blink"
        text = "Blink your eyes"
    elif index == 3:
        foreground = foreground + "angry"
        text = "Angry face"
    elif index == 4:
        foreground = foreground + "right"
        text = "Turn your face to the right"
    elif index == 5:
        foreground = foreground + "left"
        text = "Turn your face to the left"

    if status:
        foreground = foreground + "yes"
    else:
        foreground = foreground + "wrong"

    foreground = foreground + ".png"

    fg = cv2.imread(foreground)
    fg = imutils.resize(fg, width=300)

    taskbar = cv2.imread("visuals/taskbar.png")
    image[975:1125, 0:1500, :] = taskbar

    image[825:1125, 600:900, :] = fg[0:300, 0:300, :]
    # Overlay the text over it
    cv2.putText(image, text, (975, 1000), cv2.FONT_HERSHEY_SIMPLEX, 1 , color, 2)
    return image


# We ask a certain number of questions (limit_questions maximum questions)
for i_questions in range(0, limit_questions):
    # We choose at random a question to ask the user to do
    index_question = random.randint(0, 5)
    question = questions.question_bank(index_question)
    # We display the image on the live feed to ask the user to do the action
    # im = show_image(cam, question)
    im = display_im(cam, question, index_question, False)
    cv2.imshow('KYC Application', im)

    # We have a certain number of tries limit for each question, after which one, we consider it to be failed
    for i_try in range(limit_try):
        # Retrieve the live feed again, resize it, flip it
        ret, im = cam.read()
        im = imutils.resize(im, width=1500)
        im = cv2.flip(im, 1)

        # Temporary total count
        TOTAL_0 = TOTAL
        # Call the function detecting the liveness of the camera
        out_model = f_liveness_detection.detect_liveness(im, COUNTER, TOTAL_0)
        # Retake the values of the output model after running the liveness detection function
        TOTAL = out_model['total_blinks']
        COUNTER = out_model['count_blinks_consecutives']
        # If the total number of eye blinks is superior to the one before the update, we know that there was a blink
        # thus we can trigger the blink element to 1
        dif_blink = TOTAL - TOTAL_0
        if dif_blink > 0:
            blinks_up = 1
        else:
            blinks_up = 0

        # Not only are we checking the eye blinks, we also check if the question asked has been answered
        challenge_res = questions.challenge_result(question, out_model, blinks_up)

        # im = show_image(cam, question)
        im = display_im(cam, question, index_question, False)
        cv2.imshow('KYC Application', im)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Once the challenge_res has been updated to yes, meaning it has been triggered, we set the question to Ok
        if challenge_res == "pass":
            # im = show_image2(cam, question + " :", "ok")
            im = display_im(cam, question + ": ok", index_question, True)
            cv2.imshow('KYC Application', im)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            # We also increment the counter of consecutive yes
            counter_ok_consecutive += 1
            # Once we reach the limit of consecutive, we reset and stop the iteration, we are done
            if counter_ok_consecutive == limit_consecutive:
                counter_ok_questions += 1
                counter_try = 0
                counter_ok_consecutive = 0
                break
            else:
                continue
        # However, if the challenge fails, we return the question as a fail
        elif challenge_res == "fail":
            counter_try += 1
            im = display_im(cam, question + " : fail", index_question, False)
            cv2.imshow('KYC Application', im)
        elif i_try == limit_try - 1:
            break

    # Once we broke the loop if either we have all the consecutive good points, or reached the limit, we verify
    # if the counter of good questions correspond to the one expected
    if counter_ok_questions == limit_questions:
        # If it is, then we have successfully passed the Liveness check, and we should change the tab by pushing 'q'
        while True:
            img = display_im(cam, "", 6, True, color=(0, 0, 255))
            # We take a selfie at the moment of the liveness positive, the person would be forced to still be in front of the camera.
            # as he/she would be doing the liveness check, we'll use that shot to compare to later shots
            cv2.imwrite('images/selfie.png', img)
            im = display_im(cam, "LIVENESS SUCCESSFUL, press q", 6, True)

            cv2.imshow('KYC Application', im)
            # If we press the touch q, we go to the next step, which corresponds to the ID/selfie part
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # Destroy the current window
                cv2.destroyWindow('KYC Application')
                # Create a new Tkinter instance for the main window to be called
                root = Tk()
                my_gui = MainWindow(root)
                root.mainloop()
                break
    # In case, it failed, and we reached the number of trials, we write that the liveness
    elif i_try == limit_try - 1:
        while True:
            # Display the result text on the image
            im = display_im(cam, "LIVENESS FAIL", 6, False)
            cv2.imshow('KYC Application', im)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        break
    else:
        continue
