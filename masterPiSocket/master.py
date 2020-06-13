#!/usr/bin/env python3
# Documentation: https://docs.python.org/3/library/socket.html
import socket, json, sys, requests
from datetime import datetime
from passlib.hash import sha256_crypt
from flask import session
import socket_utils

HOST = ""    # Empty string means to listen on all IP's on the machine, also works with IPv6.
             # Note "0.0.0.0" also works but only with IPv4.
PORT = 63000 # Port to listen on (non-privileged ports are > 1023).
ADDRESS = (HOST, PORT)
IPADD = "192.168.8.168"

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(ADDRESS)
        s.listen()

        print("Listening on {}...".format(ADDRESS))
        while True:
            print("---------------------------")
            print("Waiting for Reception Pi...")
            conn, addr = s.accept()
            with conn:
                print("Connected to {}".format(addr))
                print()

                data = socket_utils.recvJson(conn)
                if("type" in data):
                    #Login
                    if(data['type'] == 'login'):
                        result = Login(data['username'], data['pass'], data['car_id'])
                        socket_utils.sendJson(conn, result)
                    #Facial Login
                    elif(data['type'] == 'face-login'):
                        result = FaceLogin(data['username'], data['car_id'])
                        socket_utils.sendJson(conn, result)
                    #Engineer Login
                    elif(data['type'] == 'eng-login'):
                        result = EngLogin(data['username'], data['car_id'])
                        socket_utils.sendJson(conn, result)
                    #Logout
                    elif(data['type'] == 'logout'):
                        result = Logout(data['username'], data['car_id'], data['bId'], data['token'])
                        socket_utils.sendJson(conn, result)
                     #Engineer Logout
                    elif(data['type'] == 'eng-comp'):
                        result = engComp(data['username'], data['car_id'], data['token'])
                        socket_utils.sendJson(conn, result)
                    #Car login - when car comes online
                    elif(data['type'] == 'carReg'):
                        result = carOnline(data['car_id'], data['lat'], data['lng'], True)
                        socket_utils.sendJson(conn, result)
                    #Car location update
                    elif(data['type'] == 'carLoc'):
                        result = updateOnly(data['car_id'], data['lat'], data['lng'])
                        socket_utils.sendJson(conn, result)
                    #Car Logout - when car goes offline
                    elif(data['type'] == 'carOff'):
                        result = carOnline(data['car_id'], data['lat'], data['lng'], False)
                        socket_utils.sendJson(conn, result)
                    else:
                        print("Type Error: {}".format(data['type']))
                        socket_utils.sendJson(conn, {"error": True, "type": "{}".format(data['type']), "msg": "Invalid Type value - {}".format(data['type'])})
                else:
                    print("No type attribute")
                    socket_utils.sendJson(conn, {"error": True, "type": "Missing", "msg": "Type Attribute missing"})


def Login(username, password, carId):
    """
    Sign In fucntion with username/password and carId.

    Args:
        username (string): The entered username
        password (string): The entered password
        carId (int): The id of the current car

    Returns:
        json: Return a json object based on valdation checks for the username and password
        ex:
        {"success": True ,"type" : string, "msg" : string, bId: string, "token": json}
        {"error": True ,"type" : string, "msg" : string}
    """
    print(f"Login - {username} [Car ID({carId})]")

    postData = {'username': username, 'password': password}
    response = requests.post(f"http://{IPADD}:5000/api/auth/login", json=postData)
    if response.status_code == 200:
        print("Successful Login")
        data = response.json()
        token = {'Authorization': 'Bearer ' + data.get('access_token')}
        bookingRes = confirmBooking(username, carId, token)
        if "success" in bookingRes:
            return {"success": True, "type": "login", "msg": f"Logged in User {username}", "bId": bookingRes['bId'], "token": token}
        if "error" in bookingRes:
            return {"error": True, "type": "login", "msg": f"No active booking for User {username}"}
    else:
        print("Failed Login - Incorrect Password")
        return {"error": True, "type": "login", "msg": "Incorrect User Credentials"}

def FaceLogin(username, carId):
    """
    Sign In fucntion with username from facial recognition and carId.

    Args:
        username (string): The entered username
        carId (int): The id of the current car

    Returns:
        json: Return a json object based on valdation checks for the username and password
        ex:
        {"success": True ,"type" : string, "msg" : string}
        {"error": True ,"type" : string, "msg" : string}
    """
    print(f"Facial Recognition Login - {username} [Car ID({carId})]")

    postData = {'username': username}
    response = requests.post(f"http://{IPADD}:5000/api/auth/mp/login", json=postData)
    if response.status_code == 200:
        print("Successful Login")
        data = response.json()
        token = {'Authorization': 'Bearer ' + data.get('access_token')}
        bookingRes = confirmBooking(username, carId, token)
        if "success" in bookingRes:
            return {"success": True, "type": "face-login", "msg": f"Logged in User {username}", "bId": bookingRes['bId'], "token": token}
        if "error" in bookingRes:
            return {"error": True, "type": "face-login", "msg": f"No active booking for User {username}"}
    else:
        print("Failed Login - Incorrect Password")
        return {"error": True, "type": "face-login", "msg": "Incorrect User Credentials"}

def EngLogin(username, carId):
    """
    Sign In fucntion with username from QR code and carId.

    Args:
        username (string): The entered username
        carId (int): The id of the current car

    Returns:
        json: Return a json object based on valdation checks for the username and password
        ex:
        {"success": True ,"type" : string, "msg" : string}
        {"error": True ,"type" : string, "msg" : string}
    """
    print(f"QR Engineer Login - {username} [Car ID({carId})]")

    postData = {'username': username}
    response = requests.post(f"http://{IPADD}:5000/api/auth/mp/login", json=postData)
    if response.status_code == 200:
        print("Successful Login")
        data = response.json()
        print()
        if data.get('type')!="ENGINEER":
            return {"error": True, "type": "eng-login", "msg": "User not an Engineer"}

        token = {'Authorization': 'Bearer ' + data.get('access_token')}
        repairRes = confirmRepair(carId, token)
        if "success" in repairRes:
            return {"success": True, "type": "eng-login", "msg": f"Logged in Engineer {username}", "token": token}
        if "error" in repairRes:
            return {"error": True, "type": "eng-login", "msg": "Car does not require service"}
    else:
        print("Failed Login - No existing engineer!")
        return {"error": True, "type": "eng-login", "msg": "Incorrect User Credentials"}

def Logout(username, carId, bId, token):
    """
    Sign out method for user. Takes in the Username, CarId and Booking up
    Updates the booking as finished if it exists

    Args:
        username (string): The entered username
        password (string): The entered password
        carId (int): The id of the current car

    Returns:
        json: Return a json object based on valdation checks for the username and password
        ex:
        {"success": True, "type": string, "msg": string}
        {"error": True, "type": string, "msg": string}
    """
    print(f"Logout - {username} [Car ID({carId})]")

    response = requests.put(f"http://{IPADD}:5000/api/person/{username}/booking/{str(bId)}", headers=token)
    if response.status_code == 200:
        print("Succesfully Logged out")
        return {"success": True, "type": "logout", "msg": f"Logged out User {username}"}
    else:
        print("Failed to Logged out")
        return {"error": True, "type": "logout", "msg": f"No booking for User {username}"}

def engComp(username, carId, token):
    """
    Sign out method for user. Takes in the Username, CarId and Booking up
    Updates the booking as finished if it exists

    Args:
        username (string): The entered username
        password (string): The entered password
        carId (int): The id of the current car

    Returns:
        json: Return a json object based on valdation checks for the username and password
        ex:
        {"success": True, "type": string, "msg": string}
        {"error": True, "type": string, "msg": string}
    """
    print(f"Logout - {username} [Car ID({carId})]")

    issue = {'issue': ""}

    response = requests.post(f"http://{IPADD}:5000/api/admin/car/{carId}/issue", headers=token, json=json.dumps(issue))
    if response.status_code == 200:
        print("Succesfully Completed Service")
        return {"success": True, "type": "eng-comp", "msg": f"Logged out Engineer {username}"}
    else:
        print("Failed to Complete Service")
        return {"error": True, "type": "eng-comp", "msg": "Failed to find service car"}


def confirmBooking(username, carId, token):
    """
    Confirm booking by iterating over users bookings and
    filter for active bookings

    Args:
        username (string): The entered username
        carId (int): The id of the current car

    Returns:
        json: Return a json object based on valdation checks for the username and password
        ex:
        {"success": True ,"bId" : int}
        {"error": True}
    """

    response = requests.get(f"http://{IPADD}:5000/api/person/{username}/booking", headers=token)
    if response.status_code == 404:
        return {"error": True}
    bookings = json.loads(response.text)
    if bookings is None:
        return {"error": True}
    for b in bookings:
        b['booking'] = json.loads(b['booking'])
        b['car'] = json.loads(b['car'])
        b['person'] = json.loads(b['person'])

    for b in bookings:
        if b['booking']['status'] == "Active" and b['car']['id'] == carId:
            if datetime.strptime(b['booking']['start_time'], "20%y-%m-%dT%H:%M:%S") < datetime.now():
                return {"success": True, "bId": b['booking']['id']}
    
    return {'error': True}

def confirmRepair(carId, token):
    """
    Confirm repair by iterating over car status and
    filter for repair statuss

    Args:
        carId (int): The id of the current car
        token (string): Access token for the API

    Returns:
        json: Return a json object based on valdation checks for the username and password
        ex:
        {"success": True}
        {"error": True}
    """

    response = requests.get(f"http://{IPADD}:5000/api/engineer/car", headers=token)
    if response.status_code != 200:
        return {"error": True}
    carData = response.json()
    for c in carData:
        if c['car']['id'] == carId:
            return {"success": True}
    
    return {'error': True}

def carOnline(carId, lat, lng, online):
    """
    Update the location of the car based on status

    Args:
        carId (int): The id of the current car
        lat (float): The current latitude
        lng (float): The current longitude

    Returns:
        json: Return a json object based on valdation checks for the update response
        ex:
        {"success": True, "type": string, "msg": string}
        {"error": True, "type": string, "msg": string}
    """

    if online == True:
        print(f"Car ID({carId}) Online Request\nLocation: Lat - {lat} Lng - {lng}")
        result = updateLocation(carId, lat, lng)
        if "success" in result:
            print(f"Success - Car ID({carId}) online")
            return {"success": True, "type": "carReg", "msg": f"Car ID({carId}) is online"}
        if "error" in result:
            print(f"Error - Car ID({carId}) location update failed")
            return {"error": True, "type": "carReg", "msg": f"Car ID({carId}) Location update failed"}
    else:
        print(f"Car ID({carId}) Offline Request\nLocation: Lat - {lat} Lng - {lng}")
        result = updateLocation(carId, lat, lng)
        if "success" in result:
            print(f"Success - Car ID({carId}) Offline")
            return {"success": True, "type": "carOff", "msg": f"Car ID({carId}) is offline"}
        if "error" in result:
            print(f"Error - Car ID({carId}) location update failed")
            return {"error": True, "type": "carOff", "msg": f"Car ID({carId}) Location update failed"}

def updateOnly(carId, lat, lng):
    """
    Async update function call

    Args:
        carId (int): The id of the current car
        lat (float): The current latitude
        lng (float): The current longitude

    Returns:
        json: Return a json object based on valdation checks for the update response
        ex:
        {"success": True, "type": string, "msg": string}
        {"error": True, "type": string, "msg": string}
    """
    print(f"Car ID({carId}) Location Update Request\nLocation: Lat - {lat} Lng - {lng}")

    result = updateLocation(carId, lat, lng)
    if "success" in result:
        print(f"Success - Car ID({carId}) Location updated")
        return {"success": True, "type": "carLoc", "msg": f"Car ID({carId}) location updated"}
    if "error" in result:
        print(f"Error - Car ID({carId}) location update failed")
        return {"error": True, "type": "carLoc", "msg": f"Car ID({carId}) Location update failed"}
    

def updateLocation(carId, lat, lng):
    """
    Update Car location method call

    Args:
        carId (int): The id of the current car
        lat (float): The current latitude
        lng (float): The current longitude

    Returns:
        json: Return a json object based on valdation checks for the update response
        ex:
        {"success": True}
        {"error": True}
    """

    initPayload = ({'latitude': lat, 'longitude': lng})
    payload = json.dumps(initPayload)
    response = requests.put(f"http://{IPADD}:5000/api/car/{carId}/location", data={'latitude': lat, 'longitude': lng})
    if response.status_code == 200:
        return {"success": True}
    else:
        return {"error": True}

# Execute program.
if __name__ == "__main__":
    main()
