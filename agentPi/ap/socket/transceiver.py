#IoT Assignment 2 - COSC2755
#Created by:
#   Samit Sharma
#   s3752136
#   03/05/2020
#   Agent Pi Transmit and Receive Class file

import socket, json, sys
import ap.socket.socket_utils as socket_utils

class Transceiver:

    def __init__(self):
        super().__init__()
        self.__readConfig()

    def __readConfig(self):
        """
            Read Master Pi connection information and initialise socket

            Args:
                None

            Returns:
                None
        """

        try:
            with open("ap/socket/connection.json", "r") as file:
                data = json.load(file)
                self.HOST = data["masterpi_ip"]
                self.PORT = 63000
                self.ADDRESS = (self.HOST, self.PORT)
        except IOError:
            print("File not accessible")
            self.HOST = "127.0.0.1"
            self.PORT = 63000
            self.ADDRESS = (self.HOST, self.PORT)

    def send(self, data):
        """
        Read Master Pi connection information and initialise socket

        Args:
            data (json): The information to be sent to the Master Pi
            ex [login]: {"type": 'login', "username": string, "hPass": string, "dateTime": string, "car_id": int}

        Returns:
            json: Response information from the Master Pi socket
            ex [login]: {"success": True, "type": string, "msg": string} or {"error": True, "type": string, "msg": string}
        """
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("\n----- Socket -----\n")
            print("Connecting to Master Pi...")
            try:
                s.connect(self.ADDRESS)
            except socket.error as e:
                print("Connection err: %s" %e)
                return {"error": True, "type": "connection", "msg": "{}".format(e)}
            print("Connected.\n")

            self.printOut(data)
            socket_utils.sendJson(s, data)

            print("Waiting for Master Pi...\n")
            while(True):
                object = socket_utils.recvJson(s)
                self.__checkReturn(object)
                print()
                return object

    def __checkReturn(self, data):
        """
        Reads the data from the Master Pi and checks for 'success' or 'error' in the data

        Args:
            data (json): The information to be sent to the Master Pi
            ex [login]: {"success": True, "type": string, "msg": string} or {"error": True, "type": string, "msg": string}

        Returns:
            None
        """

        if("success" in data):
            print("Success Received")
            self.__returnAction(data)
        elif("error" in data):
            print("Error from MP - {}".format(data['msg']))
        else:
            print("Invalid Data from MP")
            print(data)

    def __returnAction(self, data):
        """
        Reads the data from the Master Pi and produces an output based on the 'type' data

        Args:
            data (json): The information to be sent to the Master Pi
            ex [login]: {"success": True, "type": string, "msg": string} or {"error": True, "type": string, "msg": string}

        Returns:
            None
        """

        if(data['type'] == "login" or data['type'] == "face-login"):
            print("Unlocking Car")
        elif(data['type'] == "logout"):
            print("Locking Car")
        elif(data['type'] == "eng-login"):
            print("Service Initiated")
        elif(data['type'] == "eng-comp"):
            print("Service Complete")
        else:
            print("Car Update Done")

    def printOut(self, data):
        """
        Reads the current data and prints out the appropriate message based on the 'type' of data

        Args:
            data (json): The information to be sent to the Master Pi
            ex [login]: {"type": 'login', "username": string, "hPass": string, "dateTime": string, "car_id": int}

        Returns:
            None
        """

        if('type' in data):
            if(data['type'] == 'login'):
                print("Logging in as {}".format(data["username"]))
            elif(data['type'] == 'face-login'):
                print("Logging in as {}".format(data["username"]))
            elif(data['type'] == 'eng-login'):
                print("Logging in Engineer {}".format(data["username"]))
            elif(data['type'] == 'logout'):
                print("Logging out {}".format(data["username"]))
            elif(data['type'] == 'eng-comp'):
                print("Completing Service for {}".format(data["username"]))
            elif(data['type'] == 'carReg'):
                print("Logging In Car ID({})".format(data["car_id"]))
            elif(data['type'] == 'carLoc'):
                print("Updating Location - Car ID({})".format(data["car_id"]))
            elif(data['type'] == 'carOff'):
                print("Loggin out Car ID({})".format(data["car_id"]))
            else:
                print("Invalid Type Data")
        else:
            print("Invalid Data Object. No Type Attribute")