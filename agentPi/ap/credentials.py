#IoT Assignment 2 - COSC2755
#Created by:
#   Samit Sharma
#   s3752136
#   03/05/2020
#   Agent Pi Credentials Class

import os
from datetime import datetime
from ap.socket.transceiver import Transceiver
from ap.facialRec.facial import Facial

class Credentials:

    def __init__(self):
        super().__init__()
        self.__user_username = ""
        self.__user_exists = False
        self.__bookingId = 0
        self.__trans = Transceiver()
        self.__facial = Facial()

    def signIn(self, username, password, carId):
        """
        Sign In fucntion with username/password

        Args:
            username (string): The entered username
            password (string): The entered password
            carId (int): The id of the current car

        Returns:
            json: Return a json object from the Transciever class with the appropriate result or error based on the entered details
                ex [login]: {"success": True ,"type" : string, "msg" : string}
                            {"error": True ,"type" : string, "msg" : string}
        """

        if (self.__user_exists == False):
            res = self.__sendCreds(username, password, carId)
            if("success" in res):
                self.__user_exists = True
                self.__bookingId = res['bId']
            return res
        else:
            return {"error": True ,"type" : "login", "msg" : "Current Login Already Exists"}

    #For now return Hash - Later will have to check with DB
    def __sendCreds(self, username, password, carId):
        self.__user_username = username
        data = {"type": "login", "username": username, "pass": password, "dateTime": datetime.now().isoformat(), "car_id": carId}
        return self.__trans.send(data)

    def faceSignIn(self, username, carId):
        """
        Facial Recognition Sign In fucntion with username/password

        Args:
            username (string): The entered username
            carId (int): The id of the current car

        Returns:
            json: Return a json object from the Transciever class with the appropriate result or error based on the recognised face
                ex [login]: {"success": True ,"type" : string, "msg" : string}
                            {"error": True ,"type" : string, "msg" : string}
        """

        if (self.__user_exists == False):
            if not os.path.exists("ap/facial_rec/dataset/{}/".format(username)):
                return {"unreg": True, "msg": "Not a registered users"}
            res = self.__facial.recognize()
            if "success" in res:
                if(res['name'] == username):
                    data = {"type": "face-login", "username": username, "dateTime": datetime.now().isoformat(), "car_id": carId}
                    res2 = self.__trans.send(data)
                    if "success" in res2:
                        self.__user_exists = True
                        self.__user_username = username
                        self.__bookingId = res2['bId']
                    return res2
            elif "error" in res:
                return res
        else:
            return {"error": True ,"type" : "face-login", "msg" : "Current Login Already Exists"}

    def faceReg(self):
        """
        Facial Recognition Registration

        Args:
            None

        Returns:
            json: Return a json object from the Facial recognition class with the appropriate result or
            error based on the outcome of registering a face
                ex [login]: {"success": True ,"type" : string, "msg" : string}
                            {"error": True ,"type" : string, "msg" : string}
        """

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

    def signOut(self, carId):
        """
        Sign out of the current account

        Args:
            None

        Returns:
            json: Return a json object from the Transciever Class class with the appropriate result or
            error based on the outcome of logging out a current user
                ex [login]: {"success": True ,"type" : string, "msg" : string}
                            {"error": True ,"type" : string, "msg" : string}
        """

        if self.__user_exists == True:
            print("Logging out user")
            data = {"type": "logout", "username": self.__user_username, "dateTime": datetime.now().isoformat(), "car_id": carId, "bId": self.__bookingId}
            res = self.__trans.send(data)
            if("success" in res):
                self.__user_username = ""
                self.__user_exists = False
            return res
        else:
            return {"error": True, "type": "logout", "msg": "User logged in"}