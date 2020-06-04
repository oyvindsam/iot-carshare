#IoT Assignment 2 - COSC2755
#Implemented by:
#   Samit Sharma
#   s3752136
#   03/05/2020
#   Agent Pi Facial Recognition Class

## Acknowledgement
## This code is adapted from:
## https://www.hackster.io/mjrobot/real-time-face-recognition-an-end-to-end-project-a10826

# import the necessary packages
import cv2
import os
from imutils import paths, resize
import face_recognition
import pickle
from imutils.video import VideoStream
import time

class Facial:
  def __init__(self):
    super().__init__()

  def registerFace(self, name):
    """
    Register User for facial recognition

    Args:
        name (string): The username for capturing images

    Returns:
        dict: {'success': True, 'msg': string} or {'error': True, 'msg': string}
    """

    folder = "ap/facial_rec/dataset/{}".format(name)

    # Create a new folder for the new name
    if not os.path.exists(folder):
      os.makedirs(folder)

    # Start the camera
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)

    # Get the pre-built classifier that had been trained on 3 million faces
    classifier = "ap/facial_rec/haarcascade_frontalface_default.xml"
    if not os.path.exists(classifier):
      return {"error": True, "msg": "Face detection error - Missing classifier file"}
    
    face_detector = cv2.CascadeClassifier(classifier)

    img_counter = 0
    print("3 Pictures are required to register\n")
    while img_counter < 3:
        key = input("Press ENTER to take picture {}".format(img_counter + 1))
        
        ret, frame = cam.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        if(len(faces) == 0):
            print("No face detected, please try again")
            continue
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            img_name = "{}/{:04}.jpg".format(folder, img_counter)
            cv2.imwrite(img_name, frame[y : y + h, x : x + w])
            print("{} written!".format(img_name))
            img_counter += 1

    cam.release()
    return {"success": True, "msg": "Successfully Registered"}
  #End of registerFace(name)

  def trainModel(self):
    """
    Encodes/trains the dataset a for later use with recognition

    Args:
        None

    Returns:
        dict: {'success': True, 'msg': string} or {'error': True, 'msg': string}
    """

    # Check if dataset exists
    if not os.path.exists("ap/facial_rec/dataset"):
      return {"error": True, "msg": "No registered users"}

    print("[INFO] Training model with dataset")
    imagePaths = list(paths.list_images("ap/facial_rec/dataset"))

    knownEncodings = []
    knownNames = []

    for (i, imagePath) in enumerate(imagePaths):
        print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
        name = imagePath.split(os.path.sep)[-2]

        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb, model = "hog")

        encodings = face_recognition.face_encodings(rgb, boxes)
        
        for encoding in encodings:
            # add each encoding + name to our set of known names and encodings
            knownEncodings.append(encoding)
            knownNames.append(name)

    data = { "encodings": knownEncodings, "names": knownNames }

    with open("ap/facial_rec/encodings.pickle", "wb") as f:
        f.write(pickle.dumps(data))
    
    print("[INFO] Finished Training")
    return {"success": True, "msg": "Encoded all registered users"}
  #End of TrainModel()

  def recognize(self):
    """
    Recognise face from frame with encodings

    Args:
        None

    Returns:
        dict: {'success': True, 'name': string} or {'error': True, 'msg': string}
    """

    # load the known faces and embeddings
    print("[INFO] Loading Facial Recognizer")
    try:
      data = pickle.loads(open("ap/facial_rec/encodings.pickle", "rb").read())
    except IOError:
      return {"error": True, "msg": "Facial Recognition Failed to Load - No Encodings"}

    print("[INFO] Started Camera...")
    vs = cv2.VideoCapture(0)
    vs.set(3, 640)
    vs.set(3, 480)
    time.sleep(2.0)
    exit = False
    
    while exit == False:
      # Get the current frame and check
      ret, frame = vs.read()
      if not ret:
        return {"error": True, "msg": "Camera Error - Frame Capture Issue"}
        break

      rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      rgb = resize(frame, width = 240)

      boxes = face_recognition.face_locations(rgb, model = "hog")
      encodings = face_recognition.face_encodings(rgb, boxes)
      names = []
      fName = "Unknown"

      # loop over the facial embeddings
      for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"

        # For any matches - get the name
        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            name = max(counts, key = counts.get)

        # Update foundName (fName)
        names.append(name)
        fName = name

      #Return result regardless of found or not
      print("Person found: {}".format(fName))
      exit = True
      return {"success": True, "name":fName}
      time.sleep(2.0)
    
    #Camera release
    vs.release()
  #End of Recognise