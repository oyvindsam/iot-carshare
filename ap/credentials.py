#IoT Assignment 2 - COSC2755
#Created by:
#   Samit Sharma
#   s3752136
#   03/05/2020
#   Agent Pi Credentials Class

from passlib.hash import sha256_crypt

class Credentials:

    def __init__(self):
        super().__init__()
        self.__user_email = ""
        self.__user_pass = ""
        self.__user_exists = False

    def getCreds(self):
        print("\n---Credentials---")
        if (self.user_exists == False):
            self.__user_email = input("Enter your email: ")
            self.__user_pass = input("Enter password: ")
            hashedPassword = sha256_crypt.hash(self.__user_pass)
            return { "type": "login-creds", "email": self.__user_email, "hPass": hashedPassword }
        else:
            return {"exits" : True}

    def signedIn(self):
        if (self.__user_exists == False):
            self.__user_email = True

    def signOut(self):
        self.__user_email = ""
        self.__user_pass = ""
        self.__user_exists = False       