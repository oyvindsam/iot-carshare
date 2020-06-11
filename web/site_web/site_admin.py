import json
from datetime import datetime

import requests
from flask import render_template, session, redirect, request
from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.fields.html5 import IntegerField, DateTimeField, \
    DateTimeLocalField
from wtforms.validators import InputRequired

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
    id = IntegerField(InputRequired('Need booking id'))
    person_id = IntegerField(InputRequired('Need person id'))
    car_id = IntegerField(InputRequired('Need car id'))
    start_time = DateTimeLocalField(InputRequired(message='Date wrong'), format="%Y-%m-%dT%H:%M:%S")
    end_time = DateTimeLocalField(InputRequired(message='Date wrong'), format="%Y-%m-%dT%H:%M:%S")
    status = SelectField(InputRequired('Need status'), choices=[
        ('Not active', 'Not active'),
        ('Active', 'Active'),
        ('Finished', 'Finished'),
        ('Cancelled', 'Cancelled')
    ])


@site_blueprint.route('/admin/booking/<int:id>', methods=['GET', 'POST'])
def booking_detail(id):
    form = BookingForm()
    if form.validate_on_submit():
        new_booking = {
            'id': form.id.data,
            'person_id': form.person_id.data,
            'car_id': form.car_id.data,
            'start_time': str(form.start_time.data),
            'end_time': str(form.end_time.data),
            'status': form.status.data
        }
        response = requests.put(f"{api_address}/api/booking/{form.id.data}",
                                json=json.dumps(new_booking),
                                headers=session['auth'])
        return redirect('/admin/booking')

    else:
        booking_data = requests.get(f"{api_address}/api/booking/{id}",  headers=session['auth'])
        booking = json.loads(booking_data.json())
        # Need to convert to datetime object first
        booking['start_time'] = datetime.strptime(booking['start_time'], "%Y-%m-%dT%H:%M:%S")
        booking['end_time'] = datetime.strptime(booking['end_time'], "%Y-%m-%dT%H:%M:%S")

        form = BookingForm(**booking)

        return render_template('admin/booking-detail.html', form=form)


@site_blueprint.route('/admin/booking/<int:id>/delete', methods=['POST'])
def booking_detail_delete(id):
    response = requests.delete(f"{api_address}/api/booking/{id}", headers=session['auth'])
    return redirect('/admin/booking')