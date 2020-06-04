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

    - (MP) Designed the website (booking, cancel booking etc)
    - Google calendar integration

    Oyvind Samuelsen (s3801950):

    - Setting up Restful/Flask API environment
    - Implement Appropriate restful function calls
    - Tests

    Samit Sharma (s3752136):

    - (AP) Facial Recognition
    - (MP) Socket

    Sagar Chandrakant Pardikar (s3715199):

    - (MP) Authentication / Authorization

