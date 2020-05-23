from flask import Flask, Blueprint, request, jsonify, render_template, url_for, abort, redirect
from wtforms import Form, StringField, SelectField
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import unquote, urlparse
from flask_marshmallow import Marshmallow
from flask_wtf import FlaskForm
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import datetime
import os, requests, json
import urllib
import ast
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


site = Blueprint("site", __name__)


# Client Landing webpage.
@site.route("/")
def index():
    site.register_error_handler(404, page_not_found)
    return render_template("index.html")

# @site.errorhandler(404)
# def invalid_data(e):
#     return '<h1> No data to </h1>', 404

@site.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

#booking webpage
@site.route("/bookcar", methods=["GET", "POST"])
def bookcar():
    # Use REST API.
    response = requests.get("http://127.0.0.1:5000/api/car")
    carData = json.loads(response.json())
    print(carData)
    length= len(carData)
    print(length)
    if carData is None:
        abort(404, description="Resource not found")

        return jsonify(carData)
    
    else :

        response1 = requests.get("http://127.0.0.1:5000/api/car-manufacturer")
        carManuData = json.loads(response1.json())

        response2 = requests.get("http://127.0.0.1:5000/api/car-type")
        carTypeData = json.loads(response2.json())

        response3 = requests.get("http://127.0.0.1:5000/api/car-colour")
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

#method that redirects to the booking page
# @site.route("/book", methods=["GET", "POST"])
# def book():
#     if request.method == 'POST':
#         return redirect(url_for('site.time'))
    #   if request.method == 'POST':
    #     car_id = request.form['car_id']
    #     # hard coded value, must be able to get user id from user
    #     user_id = 1
    #     user_name = 'adi'
    #     print('car_id',car_id)
    #     print('user_id',user_id)
    #     dataToSend = {'car_id':1,'person_id':1}
    #     post_url = 'http://127.0.0.1:5000/api/person/'+user_name+'/booking'
    #     print('url',post_url)
    #     header = {'content-type':'application/json'}
    #     response = requests.post(post_url, headers = header, json=dataToSend)
    #     print ('response from server', response.text)
    #     data = response.text
    #   return render_template("bookingConfirm.html", resp = data)

# method after a car has been selected to be booked
@site.route("/time/<carinfo>", methods=["GET", "POST"])
def time(carinfo):
     if request.method == 'POST':
         decoded_query = urllib.parse.unquote(carinfo)
         decode1=ast.literal_eval(decoded_query)
         return render_template("time.html", info=decode1)

# method after to add booking to google calendar
@site.route("/timeBook", methods=["GET", "POST"])
def timeBook():
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
    print(startDateTime)
    print(endDateTime)
    print(carid)
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
                'description': 'Your car booking with Novoshare with the following car details of your car: '+ make +' with registration: '+ carreg+ ' and type is: '+cartype + ' and the Hourly Rate is: ' + rate,
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
                'attendees': [
                    {'email': 'lpage@example.com'},
                    {'email': 'sbrin@example.com'},
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
    print (google_event_link)
    return render_template("confirmation.html", invite=google_event_link) 


    # This next section's code will be here

# @site.route("/mainbooking")
# def mainbooking():


#view previous bookings
@site.route("/history")
def hist():
    # Use REST API.
    return render_template("history.html")

   



