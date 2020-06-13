# Assignment 2 for Programming of Internet of Things (COSC2755)
### Members:
###   Samit Sharma (s3752136)
###   Aditya Raj (s3730562)
###   Oyvind Samuelsen (s3801950)
###   Sagar Chandrakant Pardikar (s3715199)


## Documentation
See docs/html/index.html
To generate html docs, run ```make html```
in docs/ folder. 


## Environment Setup:

### 1. To download and install pipenv :
```
pip install pipenv
```
or for MacOS
```
brew install pipenv
```

### 2. To install all dependecies :
```
pipenv shell
```
```
pipenv install
```
### 3. To run the flask server :
```
cd web
```
Edit the sql configuration in `app.py` with the host configuration of the GCP MySQL instance 
```
flask run --host=<ip address>
```
### 4. To run the master pi socket :
```
cd masterPiSocket
```
```
python3 master.py
```
### 5. To run the agent-pi system :
Edit the IP address for Master PI in: `agentPi/ap/socket/connection.json`
```
cd agentPi
```
```
python3 APmain.py
```


## Contribution :

    Aditya Raj (s3730562):

    - Designed the website (booking, cancel booking etc)
    - Google calendar integration
    - Admin Page
		- Google voice search Integration
	- Engineer page
		- Google maps Integration

    Oyvind Samuelsen (s3801950):

    - Setting up Restful/Flask API environment
    - Implement Appropriate restful function calls
    - Tests
    - Statistical data representation with google cloud studio
	- Front-end + back-end:
		- Manager
		- Engineer
		- Admin

    Samit Sharma (s3752136):

    - User Authentication
    - Facial Recognition
    - Socket
    - Engineer Authentication
		- QR code
		- Bluetooth
	- Sockets Integration

    Sagar Chandrakant Pardikar (s3715199):

    - (MP) Authentication / Authorization

