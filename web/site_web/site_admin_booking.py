import json
import requests
from datetime import datetime
from flask import render_template, session, redirect
from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.fields.html5 import IntegerField, DateTimeLocalField
from wtforms.validators import InputRequired

from site_web import site_blueprint
from site_web.flask_site import api_address


@site_blueprint.route('/admin/booking')
def booking_list():
    """
    Load bookings from api and pass to view
    Returns: view

    """
    booking_data = requests.get(f"{api_address}/api/booking",  headers=session['auth'])
    return render_template('admin/booking-list.html', booking_data=booking_data.json())


def fix_datetime(date_str):
    """
    Helper method to load formatted datetime string
    Args:
        date_str (str): string in correct datetime format

    Returns: datetime

    """
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


class BookingForm(FlaskForm):
    id = IntegerField('Id', default=-1, render_kw={'readonly': True})
    person_id = IntegerField('Person id', [InputRequired('Need person id')])
    car_id = IntegerField('Car id', [InputRequired('Need car id')])
    start_time = DateTimeLocalField('Start time',
                                    [InputRequired(message='Date wrong')],
                                    format="%Y-%m-%dT%H:%M")
    end_time = DateTimeLocalField('End time',
                                    [InputRequired(message='Date wrong')],
                                    format="%Y-%m-%dT%H:%M")
    status = SelectField('Status', [InputRequired('Need status')], choices=[
        ('Not active', 'Not active'),
        ('Active', 'Active'),
        ('Finished', 'Finished'),
        ('Cancelled', 'Cancelled')
    ])


@site_blueprint.route('/admin/booking/new', methods=['GET', 'POST'])
def booking_detail_new():
    """
    Create a new booking from form
    Returns: views, either booking_detail if form contains errors,
    or returns to booking list

    """
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
        if 'error' in response.json():
            return render_template('admin/car-detail-new.html', form=form,
                                   error=response.json()['error'])
        return render_template('admin/booking-list.html')
    return render_template('admin/booking-detail-new.html', form=form)


@site_blueprint.route('/admin/booking/<int:id>', methods=['GET', 'POST'])
def booking_detail(id):
    """
    Load and view booking
    Args:
        id (int): booking id

    Returns: booking detail view

    """
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
        if 'error' in response.json():
            return render_template('admin/booking-detail-new.html', form=form,
                                   error=response.json()['error'])
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
    """
    Endpoint to pass delete call to api
    Args:
        id (int): booking id to delete

    Returns: redirects to booking list view

    """
    response = requests.delete(f"{api_address}/api/booking/{id}", headers=session['auth'])
    return redirect('/admin/booking')