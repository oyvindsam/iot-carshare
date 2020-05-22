#IoT Assignment 2 - COSC2755
#Created by:
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

  # def testMenu(self):
  #   exit = False
  #   while exit == False:
  #     print("Choose Options:")
  #     print("1. Register")
  #     print("2. Train Model")
  #     print("3. Recognize")
  #     opt = input("Option: ")
  #     if opt == "1":
  #       name = input("Enter Username: ")
  #       res = self.registerFace(name)
  #     elif opt == "2":
  #       res = self.trainModel()
  #       if("error" in res):
  #         print(res['msg'])
  #     elif opt == "3":
  #       res = self.recognize()
  #       if("error" in res):
  #         print(res['msg'])
  #     elif opt == "exit":
  #       exit = True
  #     else:
  #       print("Invalid Option")


  def registerFace(self, name):
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
    print("3 Pictures are required to register")
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
  #End of enterFace(name)

  def trainModel(self):
    # grab the paths to the input images in our dataset
    if not os.path.exists("ap/facial_rec/dataset"):
      return {"error": True, "msg": "No registered users"}

    print("[INFO] quantifying faces...")
    imagePaths = list(paths.list_images("ap/facial_rec/dataset"))

    # initialize the list of known encodings and known names
    knownEncodings = []
    knownNames = []

    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        # extract the person name from the image path
        print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
        name = imagePath.split(os.path.sep)[-2]

        # load the input image and convert it from RGB (OpenCV ordering)
        # to dlib ordering (RGB)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        boxes = face_recognition.face_locations(rgb, model = "hog")

        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)
        
        # loop over the encodings
        for encoding in encodings:
            # add each encoding + name to our set of known names and encodings
            knownEncodings.append(encoding)
            knownNames.append(name)

    # dump the facial encodings + names to disk
    print("[INFO] serializing encodings...")
    data = { "encodings": knownEncodings, "names": knownNames }

    with open("ap/facial_rec/encodings.pickle", "wb") as f:
        f.write(pickle.dumps(data))
    
    return {"success": True, "msg": "Encoded all registered users"}
  #End of TrainModel()

  def recognize(self):
    """

    """
    # load the known faces and embeddings
    print("[INFO] loading encodings...")
    try:
      data = pickle.loads(open("ap/facial_rec/encodings.pickle", "rb").read())
    except IOError:
      return {"error": True, "msg": "Facial Recognition Failed to Load - No Encodings"}

    # initialize the video stream and then allow the camera sensor to warm up
    print("[INFO] starting video stream...")
    vs = cv2.VideoCapture(0)
    vs.set(3, 640)
    vs.set(3, 480)
    time.sleep(2.0)
    exit = False
    # loop over frames from the video file stream
    while exit == False:
      # grab the frame from the threaded video stream
      ret, frame = vs.read()
      if not ret:
        return {"error": True, "msg": "Camera Error - Frame Capture Issue"}
        break

      # convert the input frame from BGR to RGB then resize it to have
      # a width of 750px (to speedup processing)
      rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      rgb = resize(frame, width = 240)

      # detect the (x, y)-coordinates of the bounding boxes
      # corresponding to each face in the input frame, then compute
      # the facial embeddings for each face
      boxes = face_recognition.face_locations(rgb, model = "hog")
      encodings = face_recognition.face_encodings(rgb, boxes)
      names = []
      fName = "Unknown"

      # loop over the facial embeddings
      for encoding in encodings:
          # attempt to match each face in the input image to our known
          # encodings
          matches = face_recognition.compare_faces(data["encodings"], encoding)
          name = "Unknown"

          # check to see if we have found a match
          if True in matches:
              # find the indexes of all matched faces then initialize a
              # dictionary to count the total number of times each face
              # was matched
              matchedIdxs = [i for (i, b) in enumerate(matches) if b]
              counts = {}

              # loop over the matched indexes and maintain a count for
              # each recognized face face
              for i in matchedIdxs:
                  name = data["names"][i]
                  counts[name] = counts.get(name, 0) + 1

              # determine the recognized face with the largest number
              # of votes (note: in the event of an unlikely tie Python
              # will select first entry in the dictionary)
              name = max(counts, key = counts.get)

          # update the list of names
          names.append(name)
          fName = name

      # loop over the recognized faces
      print("Person found: {}".format(fName))
      exit = True
      return {"success": True, "name":fName}
      time.sleep(2.0)
    
    # do a bit of cleanup
    vs.release()
  #End of Recognise