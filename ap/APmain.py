#IoT Assignment 2 - COSC2755
#Created by:
#   Samit Sharma
#   s3752136
#   03/05/2020
#   Agent Pi Main Class file

from AP.credentials import Credentials
from AP.socket.transceiver import Transceiver

class APMain:

    @staticmethod
    def main():
        exit = False

        trans = Transceiver()
        credsClass = Credentials()

        print("-----Welcome to the Car Menu-----")
        while exit==False:
            
            print("Choose method of authentication")
            print("1. Enter Credentials")
            print("2. Facial Recognitiobn")
            opt = input("Option: ")
            
            if (opt == "1"):
                userJson = credsClass.signIn()
                if ("exits" in userJson):
                    print("User already Logged In")
                else:
                    outcome = trans.login(userJson)
                    if (outcome == True):
                        credsClass.signedIn()
                    else:
                        credsClass.signOut()
            
            elif (opt == "2"):
                print("\n---Facial Recognition---")
                print("Not available - Under Development")
            elif (opt.lower() == "exit"):
                print("System shutting down...")
                exit = True
            else:
                print("Invalid Option!")

            print("\n")

APMain.main()