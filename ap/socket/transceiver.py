#IoT Assignment 2 - COSC2755
#Created by:
#   Samit Sharma
#   s3752136
#   03/05/2020
#   Agent Pi Transmit and Receive Class file

import socket, json
import AP.socket.socket_utils as socket_utils

class Transceiver:

    def __init__(self):
        super().__init__()
        self.__readConfig()

    def __readConfig(self):
        try:
            with open("connection.json", "r") as file:
                data = json.load(file)
                self.HOST = data["masterpi_ip"]
                self.PORT = 63000
                self.ADDRESS = (HOST, PORT)
        except IOError:
            print("File not accessible")

    def __connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Connecting to {}...".format(self.ADDRESS))
            s.connect(self.ADDRESS)
            print("Connected.")
            return s

    def login(self, user):
        s = self.__connect()

        print("Logging in as {}".format(user["email"]))
        socket_utils.sendJson(s, user)

        print("Waiting for Master Pi Auth...")
        while(True):
            object = socket_utils.recvJson(s)
            if("success" in object):
                if(object['success'] == True):
                    print("User Logged In")
                    print()
                    break