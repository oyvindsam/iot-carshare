#IoT Assignment 2 - COSC2755
#Created by:
#   Samit Sharma
#   s3752136
#   03/05/2020
#   Agent Pi Main Class file

from credentials import Credentials
from socket.transceiver import Transceiver

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
                email = input("Enter your email: ")
                password = input("Enter password: ")
                userJson = credsClass.signIn(email, password)
                if ("type" in userJson):
                    if(userJson['type'] == "exists"):
                        print("User already Logged In - {}".format(userJson['email']))
                    else:
                        print("Welcome {}".format(userJson['email']))
                else:
                    print("Credentials Class Error")
            elif (opt == "2"):
                print("\n---Facial Recognition---")
                print("Not available - Under Development")
            elif (opt.lower() == "exit"):
                print("System shutting down...")
                exit = True
            else:
                print("Invalid Option!")

            print("\n")

if __name__ == "__main__":
  APMain.main()