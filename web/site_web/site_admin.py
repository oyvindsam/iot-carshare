import json
from datetime import datetime

import requests
from flask import render_template, session, redirect, request
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, FloatField
from wtforms.fields.html5 import IntegerField, DateTimeField, \
    DateTimeLocalField
from wtforms.validators import InputRequired

from site_web import site_blueprint
from site_web.flask_site import api_address


@site_blueprint.route('/admin/')
def admin():
    return redirect('booking')


class CarForm(FlaskForm):
    # id is -1 for new cars
    id = IntegerField(InputRequired('Need car id'), default=-1, render_kw={'readonly': True})
    reg_number = StringField(InputRequired('Need car reg number'))
    car_manufacturer = IntegerField(InputRequired('Need manufaturer id'))
    car_colour = IntegerField(InputRequired('Need colour id'))
    car_type = IntegerField(InputRequired('Need type id'))
    seats = IntegerField(InputRequired('Need seats'))
    hour_rate = FloatField(InputRequired('Need hour rate'))
    latitude = StringField(InputRequired('Need latitude'), default='0.0')
    longitude = StringField(InputRequired('Need longitude'), default='0.0')
    issue = StringField()
    # issue_id is -1 if issue is not set
    issue_id = IntegerField(default=-1, render_kw={'readonly': True})



@site_blueprint.route('/admin/car')
def car_list():
    car_data = requests.get(f"{api_address}/api/admin/car", headers=session['auth'])
    return render_template('admin/car-list.html', car_data=json.loads(car_data.json()))


@site_blueprint.route('/admin/car/new', methods=['GET', 'POST'])
def car_detail_new():
    form = CarForm()

    if form.validate_on_submit():
        new_car = {
            'reg_number': form.reg_number.data,
            'car_manufacturer': form.car_manufacturer.data,
            'car_colour': form.car_colour.data,
            'car_type': form.car_type.data,
            'seats': form.seats.data,
            'hour_rate': form.hour_rate.data,
            'latitude': form.latitude.data,
            'longitude': form.longitude.data
        }

        response = requests.post(f"{api_address}/api/admin/car",
                                 json=json.dumps(new_car),
                                 headers=session['auth'])

        if response.status_code == 201:
            return redirect('/admin/car')
        error = response.json()['error']
        return render_template('admin/car-detail-new.html', form=form, error=error)
    return render_template('admin/car-detail-new.html', form=form)


@site_blueprint.route('/admin/car/<int:id>', methods=['GET', 'POST'])
def car_detail(id):
    form = CarForm()
    if form.validate_on_submit():
        id = form.id.data
        car = {
            'id': id,
            'reg_number': form.reg_number.data,
            'car_manufacturer': form.car_manufacturer.data,
            'car_colour': form.car_colour.data,
            'car_type': form.car_type.data,
            'seats': form.seats.data,
            'hour_rate': form.hour_rate.data,
            'latitude': form.latitude.data,
            'longitude': form.longitude.data
        }
        response = requests.put(f"{api_address}/api/admin/car/{id}",
                                json=json.dumps(car),
                                headers=session['auth'])
        if response.status_code == 200:
            # save new issue
            issue = {
                'car_id': id,
                'issue': form.issue.data
            }
            response = requests.post(f"{api_address}/api/admin/car/{id}/issue",
                                     json=json.dumps(issue),
                                     headers=session['auth'])
            # TODO: validate response
        return redirect('/admin/car')
        error = response.json()
        return render_template('admin/car-detail-new.html', form=form, error=error)
    else:
        car_data = requests.get(f"{api_address}/api/admin/car/{id}",
                                headers=session['auth'])
        car = json.loads(car_data.json())
        form = CarForm(**car)

        return render_template('admin/car-detail.html', form=form)


@site_blueprint.route('/admin/car/<int:id>/delete', methods=['POST'])
def car_detail_delete(id):
    response = requests.delete(f"{api_address}/api/admin/car/{id}", headers=session['auth'])
    return redirect('/admin/car')


@site_blueprint.route('/admin/booking')
def bookings():
    bookings_data = requests.get(f"{api_address}/api/booking",  headers=session['auth'])
    return render_template('admin/booking-history.html', bookings_data=bookings_data.json())


def fix_datetime(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


class BookingForm(FlaskForm):
    id = IntegerField(InputRequired('Need booking id'), default=-1)
    person_id = IntegerField(InputRequired('Need person id'))
    car_id = IntegerField(InputRequired('Need car id'))
    start_time = DateTimeLocalField(InputRequired(message='Date wrong'), format="%Y-%m-%dT%H:%M")
    end_time = DateTimeLocalField(InputRequired(message='Date wrong'), format="%Y-%m-%dT%H:%M")
    status = SelectField(InputRequired('Need status'), choices=[
        ('Not active', 'Not active'),
        ('Active', 'Active'),
        ('Finished', 'Finished'),
        ('Cancelled', 'Cancelled')
    ])


@site_blueprint.route('/admin/booking/new', methods=['GET', 'POST'])
def booking_detail_new():
    form = BookingForm()

    if form.validate_on_submit():
        new_booking = {
            'person_id': form.person_id.data,
            'car_id': form.car_id.data,
            'start_time': str(form.start_time.data),
            'end_time': str(form.end_time.data),
            'status': form.status.data
        }
        response = requests.post(f"{api_address}/api/booking",
                                 json=json.dumps(new_booking),
                                 headers=session['auth'])
        if response.status_code == 201:
            return redirect('/admin/booking')
        error = response.json()['error']
        return render_template('admin/booking-detail-new.html', form=form, error=error)
    return render_template('admin/booking-detail-new.html', form=form)


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
        booking['start_time'] = fix_datetime(booking['start_time'])
        booking['end_time'] = fix_datetime(booking['end_time'])

        form = BookingForm(**booking)
        return render_template('admin/booking-detail.html', form=form)


@site_blueprint.route('/admin/booking/<int:id>/delete', methods=['POST'])
def booking_detail_delete(id):
    response = requests.delete(f"{api_address}/api/booking/{id}", headers=session['auth'])
    return redirect('/admin/booking')