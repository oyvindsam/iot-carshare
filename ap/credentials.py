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
        self.__user_exists = False

    def signIn(self, email, password):
        if (self.__user_exists == False):
            self.__user_exists = True
            return self.hashCreds(email, password)
        else:
            return {"type" : "exists", "email" : self.__user_email}

    #For now return Hash - Later will have to check with DB
    def hashCreds(self, email, password):
        hashedPassword = sha256_crypt.hash(password)
        self.__user_email = email
        return { "type": "login-creds", "email": email, "hPass": hashedPassword }

    #Check if a user is already signed in
    def isSignedIn(self):
        return self.__user_exists

    #Sign out User
    def signOut(self):
        self.__user_email = ""
        self.__user_pass = ""
        self.__user_exists = False       