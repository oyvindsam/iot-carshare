#!/usr/bin/env python3
# Documentation: https://docs.python.org/3/library/socket.html
import socket, json, sys, requests
from datetime import datetime
from passlib.hash import sha256_crypt
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
                        print("Login - {} [Car ID({})]".format(data['username'], data['car_id']))
                        result = Login(data['username'], data['pass'], data['car_id'])
                        socket_utils.sendJson(conn, result)
                    #Facial Login
                    elif(data['type'] == 'face-login'):
                        print("Facial Recognition Login - {} [Car ID({})]".format(data['username'], data['car_id']))
                        result = FaceLogin(data['username'], data['car_id'])
                        socket_utils.sendJson(conn, result)
                    #Logout
                    elif(data['type'] == 'logout'):
                        print("Logout - {} [Car ID({})]".format(data['username'], data['car_id']))
                        result = Logout(data['username'], data['car_id'], data['bId'])
                        if "success" in result:
                            print("Succesfully Logged out")
                            socket_utils.sendJson(conn, {"success": True, "type": "{}".format(data['type']), "msg": "Logged out User {}".format(data['username'])})
                        if "error" in result:
                            print("Failed to Logged out")
                            socket_utils.sendJson(conn, {"error": True, "type": "{}".format(data['type']), "msg": "No booking for User {}".format(data['username'])})
                    #Car login - when car comes online
                    elif(data['type'] == 'carReg'):
                        print("Car ID({}) Online Request\nLocation: Lat - {} Lng - {}".format(data['car_id'], data['lat'], data['lng']))
                        result = updateLocation(data['car_id'], data['lat'], data['lng'])
                        if "success" in result:
                            print("Success - Car ID({}) online".format(data['car_id']))
                            socket_utils.sendJson(conn, {"success": True, "type": "{}".format(data['type']), "msg": "Car ID({}) is online".format(data['car_id'])})
                        if "error" in result:
                            print("Error - Car ID({}) location update failed".format(data['car_id']))
                            socket_utils.sendJson(conn, {"error": True, "type": "{}".format(data['type']), "msg": "Car ID({}) Location update failed".format(data['car_id'])})
                    #Car location update
                    elif(data['type'] == 'carLoc'):
                        print("Car ID({}) Location Update Request\nLocation: Lat - {} Lng - {}".format(data['car_id'], data['lat'], data['lng']))
                        result = updateLocation(data['car_id'], data['lat'], data['lng'])
                        if "success" in result:
                            print("Success - Car ID({}) Location updated".format(data['car_id']))
                            socket_utils.sendJson(conn, {"success": True, "type": "{}".format(data['type']), "msg": "Car ID({}) location updated".format(data['car_id'])})
                        if "error" in result:
                            print("Error - Car ID({}) location update failed".format(data['car_id']))
                            socket_utils.sendJson(conn, {"error": True, "type": "{}".format(data['type']), "msg": "Car ID({}) Location update failed".format(data['car_id'])})
                    #Car Logout - when car goes offline
                    elif(data['type'] == 'carOff'):
                        print("Car ID({}) Offline Request\nLocation: Lat - {} Lng - {}".format(data['car_id'], data['lat'], data['lng']))
                        result = updateLocation(data['car_id'], data['lat'], data['lng'])
                        if "success" in result:
                            print("Success - Car ID({}) Offline".format(data['car_id']))
                            socket_utils.sendJson(conn, {"success": True, "type": "{}".format(data['type']), "msg": "Car ID({}) is offline".format(data['car_id'])})
                        if "error" in result:
                            print("Error - Car ID({}) location update failed".format(data['car_id']))
                            socket_utils.sendJson(conn, {"error": True, "type": "{}".format(data['type']), "msg": "Car ID({}) Location update failed".format(data['car_id'])})
                    else:
                        print("Type Error: {}".format(data['type']))
                        socket_utils.sendJson(conn, {"error": True, "type": "{}".format(data['type']), "msg": "Invalid Type value - {}".format(data['type'])})
                else:
                    print("No type attribute")
                    socket_utils.sendJson(conn, {"error": True, "type": "Missing", "msg": "Type Attribute missing"})


def Login(username, password, carId):
    """
    Sign In fucntion with username/password and carId.
    Performs GET request to /api/person/<string:username> and does validation checks
    Then calls confirmBooking()

    Args:
        username (string): The entered username
        password (string): The entered password
        carId (int): The id of the current car

    Returns:
        json: Return a json object based on valdation checks for the username and password
        ex [login]:
        {"success": True ,"type" : string, "msg" : string}
        {"error": True ,"type" : string, "msg" : string}
    """

    response = requests.get("http://{}:5000/api/person/{}".format(IPADD, username))
    user = json.loads(response.json())
    if user is None:
        print("Failed Login - No User Registered under username")
        return {"error": True, "type": "login", "msg": "No user account for User {}".format(username)}
    else:
        if sha256_crypt.verify(password, user['password_hashed']):
            print("Successful Login")
            bookingRes = confirmBooking(username, carId)
            if "success" in bookingRes:
                return {"success": True, "type": "login", "msg": "Logged in User {}".format(username), "bId": bookingRes['bId']}
            if "error" in bookingRes:
                return {"error": True, "type": "login", "msg": "No active booking for User {}".format(username)}
        else:
            print("Failed Login - Incorrect Password")
            return {"error": True, "type": "login", "msg": "Incorrect User Credentials"}

def FaceLogin(username, carId):
    """
    Sign In fucntion with username from facial recognition and carId.
    Performs GET request to /api/person/<string:username> and does validation checks
    Then calls confirmBooking()

    Args:
        username (string): The entered username
        carId (int): The id of the current car

    Returns:
        json: Return a json object based on valdation checks for the username and password
        ex [login]:
        {"success": True ,"type" : string, "msg" : string}
        {"error": True ,"type" : string, "msg" : string}
    """

    response = requests.get("http://{}:5000/api/person/{}".format(IPADD, username))
    user = json.loads(response.json())
    if user is None:
        print("Failed Login - No User Registered under username")
        return {"error": True, "type": "login", "msg": "No user account for User {}".format(username)}
    else:
        if user['username'] == username:
            print("Successful Login")
            bookingRes = confirmBooking(username, carId)
            if "success" in bookingRes:
                return {"success": True, "type": "face-login", "msg": "Logged in User {}".format(username), "bId": bookingRes['bId']}
            if "error" in bookingRes:
                return {"error": True, "type": "login", "msg": "No active booking for User {}".format(username)}
        else:
            return {"error": True, "type": "face-login", "msg": "Username does not match"}

def Logout(username, carId, bId):
    """
    Sign out method for user. Takes in the Username, CarId and Booking up
    Updates the booking as finished if it exists

    Args:
        username (string): The entered username
        password (string): The entered password
        carId (int): The id of the current car

    Returns:
        json: Return a json object based on valdation checks for the username and password
        ex [login]:
        {"success": True}
        {"error": True}
    """

    response = requests.put("http://{}:5000/api/person/{}/booking/{}".format(IPADD, username, str(bId)))
    if response.status_code == 200:
        return {"success": True}
    else:
        return {"error": True}


def confirmBooking(username, carId):
    """
    Confirm booking by iterating over users bookings and
    filter for active bookings

    Args:
        username (string): The entered username
        carId (int): The id of the current car

    Returns:
        json: Return a json object based on valdation checks for the username and password
        ex [login]:
        {"success": True ,"bId" : int}
        {"error": True}
    """

    response = requests.get("http://{}:5000/api/person/{}/booking".format(IPADD, username))
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

def updateLocation(carId, lat, lng):
    """
    Update Car location method call

    Args:
        carId (int): The id of the current car
        lat (float): The current latitude
        lng (float): The current longitude

    Returns:
        json: Return a json object based on valdation checks for the update response
        ex [login]:
        {"success": True}
        {"error": True}
    """

    initPayload = ({'latitude': lat, 'longitude': lng})
    payload = json.dumps(initPayload)
    response = requests.put("http://{}:5000/api/car/{}/location".format(IPADD, carId), data={'latitude': lat, 'longitude': lng})
    if response.status_code == 200:
        return {"success": True}
    else:
        return {"error": True}

# Execute program.
if __name__ == "__main__":
    main()
