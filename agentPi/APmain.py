#IoT Assignment 2 - COSC2755
#Created by:
#   Samit Sharma
#   s3752136
#   03/05/2020
#   Agent Pi Main Class file

from datetime import datetime
from ap.credentials import Credentials
from ap.socket.transceiver import Transceiver
from ap.facialRec.facial import Facial

class APMain:

    @staticmethod
    def main():
        APMain.exit = False

        APMain.credsClass = Credentials()
        APMain.trans = Transceiver()
        APMain.face = Facial()

        #Initialise Car and register with system
        APMain.car_id = 1
        res = APMain.trans.send({'type': 'carReg','car_id': APMain.car_id, "lat": -37.8102361, "lng": 144.9627652, "dateTime": datetime.now().isoformat()})
        if "error" in res:
            print("Seems like Master Pi might be offline")
            return

        print("-----Welcome to the Car Menu-----")
        while APMain.exit==False:
            state = APMain.credsClass.isSignedIn()
            #No logged in user
            if (state == False):
                APMain.mainMenu()
            else:
                userType = APMain.credsClass.getType()
                if userType == "user":
                    APMain.userMenu()
                elif userType == "engineer":
                    APMain.engineerMenu()

            print("\n")

    @staticmethod
    def mainMenu():
        print("Choose An Option")
        print("1. Enter Credentials")
        print("2. Facial Recognition")
        print("3. Service Car")
        opt = input("Option: ")

        if (opt == "1"):
            APMain.credsMenu()
        elif (opt == "2"):
            APMain.faceMenu()
        elif (opt == "3"):
            APMain.engineerCred()
        elif (opt.lower() == "exit"):
            APMain.trans.send({'type': 'carOff','car_id': APMain.car_id, "lat": -37.8102361, "lng": 144.9627652})
            print("System shutting down...")
            APMain.exit = True
        else:
            print("Invalid Option!")

    @staticmethod
    def credsMenu():
        email = input("Enter your username: ")
        password = input("Enter password: ")
        user = APMain.credsClass.signIn(email, password, 1)
        if ("success" in user):
            if(user['type'] == "login"):
                APMain.updateCarLoc()
                print("Welcome {}".format(APMain.credsClass.getUserName()))
        elif("error" in user):
            print("Login Error - {}".format(user['msg']))
        else:
            print("Credentials Object Error")

    @staticmethod
    def faceMenu():
        opt = input("Enter username: ")
        res = APMain.credsClass.faceSignIn(opt, APMain.car_id)
        APMain.updateCarLoc()
        if("error" in res):
            print(res['msg'])
        elif("unreg" in res):
            print(res['msg'])
            reg = input("Would you like to register? y/n: ")
            if reg.lower() == "y":
                print("Please sign in first before registering\n")
                APMain.credsMenu()
                APMain.credsClass.faceReg()

    @staticmethod
    def userMenu():
        uName = APMain.credsClass.getUserName()
        print("{} logged in. Choose from below:".format(uName))
        print("1. Return and Logout")
        opt = input('Option: ')
        if (opt == "1"):
            APMain.updateCarLoc()
            APMain.credsClass.signOut(APMain.car_id)
        else:
            print("Invalid Option!")

    @staticmethod
    def engineerMenu():
        uName = APMain.credsClass.getUserName()
        print("{} logged in. Choose from below:".format(uName))
        print("1. Service complete and Logout")
        opt = input('Option: ')
        if (opt == "1"):
            APMain.updateCarLoc()
            APMain.credsClass.engComplete(APMain.car_id)
        else:
            print("Invalid Option!")
    
    @staticmethod
    def engineerCred():
        print("Choose method of authentication")
        print("1. QR Code")
        print("2. Bluetooth")
        print("0. Return")

        opt = input('Option: ')

        if (opt == "1"):
            APMain.credsClass.qrSignIn(APMain.car_id)
        elif (opt == "2"):
            print("To be done")
        elif (opt == "3"):
            return
        else:
            print("Invalid Option!")

    @staticmethod
    def updateCarLoc():
        res = APMain.trans.send({'type': 'carLoc','car_id': APMain.car_id, "lat": -37.8075801, "lng": 144.9567837})
        if("error" in res):
            if(res['error'] == "connection"):
                print("Failed to Connect")
        

if __name__ == "__main__":
  APMain.main()