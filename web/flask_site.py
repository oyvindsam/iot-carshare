from flask import Flask, Blueprint, request, jsonify, render_template, url_for, abort
from wtforms import Form, StringField, SelectField
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_wtf import FlaskForm
import os, requests, json



site = Blueprint("site", __name__)


# Client Landing webpage.
@site.route("/")
def index():
    return render_template("index.html")

@site.errorhandler(404)
def invalid_data(e):
    return '<h1> No data to </h1>', 404

@site.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

#booking webpage
@site.route("/bookcar", methods=["GET", "POST"])
def bookcar():
    # Use REST API.
    response = requests.get("http://127.0.0.1:5000/api/car")
    carData = json.loads(response.json())

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

        #For each car get the values from the hasmap
        for car in carData:
            manuId = car['car_manufacturer']
            car['car_manufacturer'] = carManuMap.get(manuId)

            typeId = car['car_type']
            car['car_type'] = carTypeMap.get(typeId)

            colourId = car['car_colour']
            car['car_colour'] = carColorMap.get(colourId)
                    
        return render_template("bookcar.html", cars = carData)

@site.route("/booking", methods=["POST"])
def booking():
      if request.method == 'POST':
        car_id = request.form['car_id']
        # hard coded value, must be able to get user id from user
        user_id = 1
        user_name = 'adi'
        print('car_id',car_id)
        print('user_id',user_id)
        dataToSend = {'car_id':1,'person_id':1}
        post_url = 'http://127.0.0.1:5000/api/person/'+user_name+'/booking'
        print('url',post_url)
        header = {'content-type':'application/json'}
        response = requests.post(post_url, headers = header, json=dataToSend)
        print ('response from server', response.text)
        data = response.text
      return render_template("bookingConfirm.html", resp = data)

    
#view previous bookings
@site.route("/history")
def hist():
    # Use REST API.
    return render_template("history.html")

   



