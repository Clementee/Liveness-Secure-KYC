def question_bank(index):
    """
    Bank of questions susceptible to be randomly asked the user
    :param index: Index of the question taken, called using a random index
    :return: The string corresponding the question requested
    """
    questions = [
        "smile",
        "surprise",
        "blink eyes",
        "angry",
        "turn face right",
        "turn face left"]
    return questions[index]


def challenge_result(question, out_model, blinks_up):
    """
    Verify the questions have been answered correctly by the user
    :param question: The question that was randomly chosen to be answered
    :param out_model: The output model containing the different counters noting the possible actions from the user
    :param blinks_up: The number of eye blinks noted by the trained model
    :return: The string answering whether the challenge has been
    """
    if question == "smile":
        if len(out_model["emotion"]) == 0:
            challenge = "fail"
        elif out_model["emotion"][0] == "happy":
            challenge = "pass"
        else:
            challenge = "fail"

    elif question == "surprise":
        if len(out_model["emotion"]) == 0:
            challenge = "fail"
        elif out_model["emotion"][0] == "surprise":
            challenge = "pass"
        else:
            challenge = "fail"

    elif question == "angry":
        if len(out_model["emotion"]) == 0:
            challenge = "fail"
        elif out_model["emotion"][0] == "angry":
            challenge = "pass"
        else:
            challenge = "fail"

    elif question == "turn face right":
        if len(out_model["orientation"]) == 0:
            challenge = "fail"
        elif out_model["orientation"][0] == "right":
            challenge = "pass"
        else:
            challenge = "fail"

    elif question == "turn face left":
        if len(out_model["orientation"]) == 0:
            challenge = "fail"
        elif out_model["orientation"][0] == "left":
            challenge = "pass"
        else:
            challenge = "fail"

    elif question == "blink eyes":
        if blinks_up == 1:
            challenge = "pass"
        else:
            challenge = "fail"

    return challenge
