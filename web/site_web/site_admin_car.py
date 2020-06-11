import json
import requests

from flask import render_template, session, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import InputRequired

from site_web import site_blueprint
from site_web.flask_site import api_address


class CarForm(FlaskForm):
    # id is -1 for new cars
    id = IntegerField('Id', default=-1, render_kw={'readonly': True})
    reg_number = StringField('Registration number',
                             [InputRequired('Need car reg number')])
    car_manufacturer = IntegerField('Manufacturer',
                                    [InputRequired('Need manufaturer id')])
    car_colour = IntegerField('Colour', [InputRequired('Need colour id')])
    car_type = IntegerField('Type', [InputRequired('Need type id')])
    seats = IntegerField('Seats', [InputRequired('Need seats')])
    hour_rate = FloatField('Hour rate', [InputRequired('Need hour rate')])
    latitude = StringField('Latitude', default='0.0')
    longitude = StringField('Longitude', default='0.0')
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
        else:
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

