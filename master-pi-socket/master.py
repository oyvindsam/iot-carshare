#!/usr/bin/env python3
# Documentation: https://docs.python.org/3/library/socket.html
import socket, json, sys
import socket_utils

HOST = ""    # Empty string means to listen on all IP's on the machine, also works with IPv6.
             # Note "0.0.0.0" also works but only with IPv4.
PORT = 63000 # Port to listen on (non-privileged ports are > 1023).
ADDRESS = (HOST, PORT)

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
                        socket_utils.sendJson(conn, {"success": True, "type": "{}".format(data['type']), "msg": "Logged in User {}".format(data['username'])})
                    #Login
                    elif(data['type'] == 'face-login'):
                        print("Facial Recognition Login - {} [Car ID({})]".format(data['username'], data['car_id']))
                        socket_utils.sendJson(conn, {"success": True, "type": "{}".format(data['type']), "msg": "Logged in User {}".format(data['username'])})
                    #Logout
                    elif(data['type'] == 'logout'):
                        print("Logout - {} [Car ID({})]".format(data['username'], data['car_id']))
                        socket_utils.sendJson(conn, {"success": True, "type": "{}".format(data['type']), "msg": "Logged out User {}".format(data['username'])})
                    #Car login - when car comes online
                    elif(data['type'] == 'carReg'):
                        print("Car ID({}) Online\nLocation: {}".format(data['car_id'], data['loc']))
                        socket_utils.sendJson(conn, {"success": True, "type": "{}".format(data['type']), "msg": "Car ID({}) is online".format(data['car_id'])})
                    #Car location update
                    elif(data['type'] == 'carLoc'):
                        print("Car ID({}) Location Update\nLocation: {}".format(data['car_id'], data['loc']))
                        socket_utils.sendJson(conn, {"success": True, "type": "{}".format(data['type']), "msg": "Car ID({}) location updated".format(data['car_id'])})
                    #Car Logout - when car goes offline
                    elif(data['type'] == 'carOff'):
                        print("Car ID({}) Offline\nLocation: {}".format(data['car_id'], data['loc']))
                        socket_utils.sendJson(conn, {"success": True, "type": "{}".format(data['type']), "msg": "Car ID({}) is offline".format(data['car_id'])})
                    else:
                        print("Type Error: {}".format(data['type']))
                        socket_utils.sendJson(conn, {"error": True, "type": "{}".format(data['type']), "msg": "Invalid Type value - {}".format(data['type'])})
                else:
                    print("No type attribute")
                    socket_utils.sendJson(conn, {"error": True, "type": "Missing", "msg": "Type Attribute missing"})

# Execute program.
if __name__ == "__main__":
    main()
