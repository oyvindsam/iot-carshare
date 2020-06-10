import json
from datetime import datetime

import requests
from flask import render_template, session, redirect, request
from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.fields.html5 import IntegerField, DateTimeField, \
    DateTimeLocalField

from site_web import site_blueprint
from site_web.flask_site import api_address


@site_blueprint.route('/admin/')
def admin():
    return redirect('booking')


@site_blueprint.route('/admin/booking')
def bookings():
    bookings_data = requests.get(f"{api_address}/api/booking",  headers=session['auth'])

    return render_template('admin/booking-history.html', bookings_data=bookings_data.json())


class BookingForm(FlaskForm):
    id = IntegerField()
    person_id = IntegerField()
    car_id = IntegerField()
    start_time = DateTimeLocalField(format="%Y-%m-%dT%H:%M:%S")
    end_time = DateTimeLocalField(format="%Y-%m-%dT%H:%M:%S")
    status = SelectField(choices=[
        ('Not active', 'Not active'),
        ('Active', 'Active'),
        ('Finished', 'Finished'),
        ('Cancelled', 'Cancelled')
    ])


@site_blueprint.route('/admin/booking/<int:id>')
def booking_detail(id):

    if request.method == 'GET':
        booking_data = requests.get(f"{api_address}/api/booking/{id}",  headers=session['auth'])
        booking = json.loads(booking_data.json())
        # Need to convert to datetime object first
        booking['start_time'] = datetime.strptime(booking['start_time'], "%Y-%m-%dT%H:%M:%S")
        booking['end_time'] = datetime.strptime(booking['end_time'], "%Y-%m-%dT%H:%M:%S")

        form = BookingForm(**booking)

        return render_template('admin/booking-detail.html', form=form)

    elif request.method == 'POST':
        form = BookingForm()
        data = request.get_json()
