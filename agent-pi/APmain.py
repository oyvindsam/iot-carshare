#IoT Assignment 2 - COSC2755
#Created by:
#   Samit Sharma
#   s3752136
#   03/05/2020
#   Agent Pi Main Class file

from ap.credentials import Credentials
from ap.socket.transceiver import Transceiver

class APMain:

    @staticmethod
    def main():
        exit = False
        trans = Transceiver()
        credsClass = Credentials()

        #Initialise Car and register with system
        # carId = "1"
        # trans.regCar({'type': 'car-reg','id': carId, "loc": {"lat": 0, "lng": 0}})

        print("-----Welcome to the Car Menu-----")
        while exit==False:
            state = credsClass.isSignedIn()
            #No logged in user
            if (state == False):
                APMain.printMenu()
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
                            print("Car Unlocked")
                            trans.login(userJson)
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

            else:
                uName = credsClass.getUserName()
                APMain.printUserMenu(uName)
                opt = input('Option: ')
                if (opt == "1"):
                    print("Logging out user")
                    trans.logout({'type': 'logout', 'email': uName})
                    credsClass.signOut()
                    print("Car Locked")
                else:
                    print("Invalid Option!")
            
            

            print("\n")

    @staticmethod
    def initMenu():
        print()

    @staticmethod
    def printMenu():
        print("Choose method of authentication")
        print("1. Enter Credentials")
        print("2. Facial Recognitiobn")

    @staticmethod
    def printUserMenu(username):
        print("{} logged in. Choose from below:".format(username))
        print("1. Return and Logout")

if __name__ == "__main__":
  APMain.main()