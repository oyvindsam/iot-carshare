import ast
import base64
import json
import os
import os.path
import pickle
import urllib
from urllib.parse import unquote, urlparse, parse_qs

import requests
from flask import request, jsonify, render_template, abort, session
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from oauth2client import file

from site_web import site_blueprint

api_address = 'http://127.0.0.1:5000'


# Client Landing webpage.
@site_blueprint.route('/')
def index():
    return render_template('index.html')


# method for the webpage through which the user can book cars
@site_blueprint.route("/bookcar", methods=["GET", "POST"])
def bookcar():
    # Use REST API.
    """
        Displaying all the available cars from the database
    """

    response = requests.get(f"{api_address}/api/car", headers=session.get('auth', None))
    if response.status_code == 401:
        return abort(401)
    carData = json.loads(response.json())
    length = len(carData)
    if carData is None:
        abort(404, description="Resource not found")

        return jsonify(carData)
    
    else :

        response1 = requests.get(f"{api_address}/api/car-manufacturer", headers=session.get('auth', None))
        carManuData = json.loads(response1.json())

        response2 = requests.get(f"{api_address}/api/car-type", headers=session.get('auth', None))
        carTypeData = json.loads(response2.json())

        response3 = requests.get(f"{api_address}/api/car-colour", headers=session.get('auth', None))
        carColorData = json.loads(response3.json())

        #preprocess using hashmap
        carManuMap = dict()
        carTypeMap = dict()
        carColorMap = dict()

        #Fill each hashmap
        for manu in carManuData:
            carManuMap[manu['id']] = manu['manufacturer']

        for t in carTypeData:
            carTypeMap[t['id']] = t['type']
        
        for color in carColorData:
            carColorMap[color['id']] = color['colour']
        index = 1
        
        #For each car get the values from the hasmap
        for car in carData:
            manuId = car['car_manufacturer']
            car['car_manufacturer'] = carManuMap.get(manuId)

            typeId = car['car_type']
            car['car_type'] = carTypeMap.get(typeId)

            colourId = car['car_colour']
            car['car_colour'] = carColorMap.get(colourId)
            car['index'] = index
            index = index + 1
                    
        return render_template("bookcar.html", cars = carData, leng=length)



# method after a car has been selected to be booked
@site_blueprint.route("/time/<carinfo>", methods=["GET", "POST"])
def time(carinfo):
     """
        Parsing the json string which is retrieved from the available cars page
        and decoding it using: urllib.parse.unquote, to convert it into a parsable string so that it can be read 
    """
     if request.method == 'POST':
         decoded_query = urllib.parse.unquote(carinfo)
         decode1=ast.literal_eval(decoded_query)
         return render_template("time.html", info=decode1)

# method after to add booking to google calendar
@site_blueprint.route("/timeBook", methods=["GET", "POST"])
def timeBook():

    """
        Adding the google calendar event and updating the new booking to the database
    """
    carid = request.form['car_id']
    make = request.form['make']
    cartype = request.form['type']
    carreg = request.form['reg']
    rate = request.form['rate']
    longitude = request.form['longitude']
    latitude = request.form['latitude']
    location= 'http://www.google.com/maps/place/'+latitude+','+longitude
    startDateTime = request.form['bookingstarttime']
    endDateTime = request.form['bookingendtime']
    startDateTime = startDateTime + ':00+10:00'
    endDateTime = endDateTime + ':00+10:00'

    username = session['person']['username']
    email = session['person']['email']

    if startDateTime < endDateTime :

        SCOPES = ["https://www.googleapis.com/auth/calendar"]
        store = file.Storage('token.json')
        creds = None

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        event = {
                    'summary': 'Novo Car share booking',
                    'location': location,
                    'description': 'Your car booking with Novoshare booked by user '+ username +' with email '+ email +' with the following car details of your car: '+ make +' with registration: '+ carreg+ ' and type is: '+cartype + ' and the Hourly Rate is: ' + rate,
                    'start': {
                        'dateTime': startDateTime,
                        'timeZone': "Australia/Melbourne",
                    },
                    'end': {
                        'dateTime': endDateTime,
                        'timeZone': "Australia/Melbourne",
                    },
                    'recurrence': [
                        'RRULE:FREQ=DAILY;COUNT=2'
                    ],
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                        ],
                    },
                    }
        event = service.events().insert(calendarId='primary', body=event).execute()
        google_event_link = event.get('htmlLink')

        parsed = urlparse(google_event_link)
        google_event_id = parse_qs(parsed.query)['eid'][0]
        print(google_event_id)
        initload = ({
            'car_id': carid,
            'person_id': username,
            'start_time': startDateTime,
            'end_time': endDateTime,
            'google_calendar_id': google_event_id,
        })

        #prepping the payload for a POST request
        payload = json.dumps(initload)
        url = requests.post(f"{api_address}/api/person/{username}/booking", json=payload, headers=session.get('auth', None))

        return render_template("confirmation.html", invite=google_event_link)

    else :
        return render_template("timerror.html")


# method for webpage to view previous bookings
@site_blueprint.route("/history", methods=["GET", "POST"])
def history():
    """
        Retrieval of all the past and current bookings from the database, 
        shows the person username, car id and for what duration it was booked
    """
    username = session['person']['username']
    response_book = requests.get(f"{api_address}/api/person/{username}/booking",
                                 headers=session['auth'])
    responder = json.loads(response_book.text)

    # preprocess the string object 

    for bookings in responder:
        bookings['booking'] = json.loads(bookings['booking'])
        bookings['car'] = json.loads(bookings['car'])
        bookings['person'] = json.loads(bookings['person'])

    return render_template("history.html", bookings = responder)

# method after selction of booking to be canceled is selected
@site_blueprint.route("/cancel", methods=["POST"])
def cancel():

    """
    Conversion of the bookinfo json string which is retrieved from the history page,
    using ast so that it can be passed into the next page
    """
    cancel = {}
    cancel['bookingID'] = request.form['bookingId']
    cancel["googleID"] = request.form['gid']
    cancel["cid"] = request.form['cid']
    cancel["start_time"] = request.form['starttime']
    cancel["end_time"] = request.form['endtime']
    cancel["status"] = request.form['bstatus']
    return render_template("cancel.html", info=cancel)

# method with which booking is canceled
@site_blueprint.route('/cancelbook', methods=['POST'])
def cancelbook():

    """
    Passing parameters such as the booking ID of a particular booking and the user name
    of the user to do a DELETE request which updates the bookings with the booking which was cancelled
    """

    calID = request.form['googleid']
    bookingID = request.form['bookingId']
    usrName = request.form['username']
    decoder = base64.b64decode(calID+'=').decode('utf-8')
    decoder = decoder.split()
    calID = decoder[0]
    str(bookingID)
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    store = file.Storage('token.json')
    creds = None

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    response = service.events().delete(calendarId='primary', eventId = calID).execute()
    #print(response)
    username = session['person']['username']
    url = f"{api_address}/api/person/{username}/booking/{bookingID}"
    response = requests.delete(url, headers=session['auth'])
    return render_template("cancelled.html")




 

 



 

   



