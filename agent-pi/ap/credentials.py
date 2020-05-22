#IoT Assignment 2 - COSC2755
#Created by:
#   Samit Sharma
#   s3752136
#   03/05/2020
#   Agent Pi Credentials Class

import os
from datetime import datetime
from passlib.hash import sha256_crypt
from ap.socket.transceiver import Transceiver
from ap.facial_rec.facial import Facial

class Credentials:

    def __init__(self):
        super().__init__()
        self.__user_username = ""
        self.__user_exists = False
        self.__trans = Transceiver()
        self.__facial = Facial()

    def signIn(self, username, password, carId):
        if (self.__user_exists == False):
            self.__user_exists = True
            res = self.__hashCreds(username, password, carId)
            return res
        else:
            return {"error": True ,"type" : "login", "msg" : "Current Login Already Exists"}

    #For now return Hash - Later will have to check with DB
    def __hashCreds(self, username, password, carId):
        hashedPassword = sha256_crypt.hash(password)
        self.__user_username = username
        data = {"type": "login", "username": username, "hPass": hashedPassword, "dateTime": datetime.now().isoformat(), "car_id": carId}
        return self.__trans.send(data)

    def faceSignIn(self, username, carId):
        if (self.__user_exists == False):
            if not os.path.exists("ap/facial_rec/dataset/{}/".format(username)):
                return {"unreg": True, "msg": "Not a registered users"}
            res = self.__facial.recognize()
            if "success" in res:
                if(res['name'] == username):
                    self.__user_exists = True
                    self.__user_username = username
                    data = {"type": "face-login", "username": username, "dateTime": datetime.now().isoformat(), "car_id": carId}
                    return self.__trans.send(data)
            elif "error" in res:
                return res
        else:
            return {"error": True ,"type" : "face-login", "msg" : "Current Login Already Exists"}

    def faceReg(self):
        if (self.__user_exists == True):
            res = self.__facial.registerFace(self.__user_username)
            if "error" in res:
                print(res['msg'])
                return
            res2 = self.__facial.trainModel()
            if "error" in res2:
                print(res2['msg'])
        else:
            return {"error": True ,"type" : "face-reg", "msg" : "No User Logged In"}

    #Check if a user is already signed in
    def isSignedIn(self):
        return self.__user_exists

    def getUserName(self):
        return self.__user_username

    #Sign out User
    def signOut(self, carId):
        print("Logging out user")
        data = {"type": "logout", "username": self.__user_username, "dateTime": datetime.now().isoformat(), "car_id": carId}
        res = self.__trans.send(data)
        if("success" in res):
            self.__user_username = ""
            self.__user_exists = False
        return res