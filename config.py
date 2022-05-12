# -------------------------------------- profile_detection ---------------------------------------

detect_frontal_face = 'profile_detection/haarcascades/haarcascade_frontalface_alt.xml'
detect_profile_face = 'profile_detection/haarcascades/haarcascade_profileface.xml'

# -------------------------------------- emotion_detection ---------------------------------------
# Path for the emotional detection model
path_model = 'emotion_detection/Models/model_dropout.hdf5'

# Parameters of the model, the image need to be converted to a canvas of 48x48 in gray scales
w, h = 48, 48
rgb = False
labels = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# The number of frames consecutive to consider a blink
EYE_AR_THRESH = 0.23  # baseline
EYE_AR_CONSEC_FRAMES = 1

# Eye landmarks
eye_landmarks = "blink_detection/model_landmarks/shape_predictor_68_face_landmarks.dat"
