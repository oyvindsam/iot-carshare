#IoT Assignment 2 - COSC2755
#Created by:
#   Samit Sharma
#   s3752136
#   11/05/2020
#   Agent Pi Credentials Class Unit Test

import unittest, sys
from passlib.hash import sha256_crypt
sys.path.append("..")
from credentials import Credentials

class TestCredentials(unittest.TestCase):

  def setUp(self):
    self.credsClass = Credentials()

  def test_1checkHash(self):
    print("Test - Hashed Password")
    #Check return of hashCreds(email, password)
    testPass = self.credsClass.hashCreds('test@email.com', 'password123')
    self.assertTrue(sha256_crypt.verify('password123', testPass['hPass']), "Password Test Failed - Unmatched Hashed Password!")

  def test_2signIn(self):
    print("Test - Sign In")
    #Sign In user once
    testSign = self.credsClass.signIn("test@email.com", 'password123')
    #Check for SignedIn Status, the return 'email' and 'hPass' (Hashed Password)
    self.assertEqual(self.credsClass.isSignedIn(), True, "Sign In Error - Signed In status not updated")
    self.assertEqual(testSign['email'], "test@email.com", "Sign In Error - Signed In email not updated")
    self.assertTrue(sha256_crypt.verify('password123', testSign['hPass']), "Sign In Error - Unmatched Hashed Password!")

  def test_3signInAgain(self):
    print("Test - Sign In again")
    #Try Sign in Twice and check the 2nd return
    self.credsClass.signIn("test@email.com", 'password123')
    testAgain = self.credsClass.signIn("test2@email.com", 'password1234')
    #Check for SignedIn Status, the return 'type' and 'email'
    self.assertEqual(self.credsClass.isSignedIn(), True, "Sign In Again Error - Signed In status not updated")
    self.assertEqual(testAgain['type'], "exists", "Sign In Again Error - Signed In status not updated, returning incorrect object")
    self.assertNotEqual(testAgain['email'], "test2@email.com", "Sign In Again Error - Signed In email not updated")
  
  def test_4signOut(self):
    print("Test - Sign Out")
    #Sign in user and check signed in
    self.credsClass.signIn("test@email.com", 'password123')
    self.assertEqual(self.credsClass.isSignedIn(), True, "Sign In Error - Signed In status not updated")
    #Sign out user and checked signed out
    self.credsClass.signOut()
    self.assertEqual(self.credsClass.isSignedIn(), False, "Sign Out Error - Signed In status not updated")

  def tearDown(self):
    self.credsClass = None


if __name__ == "__main__":
    unittest.main()