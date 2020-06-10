import json

import requests
from flask import render_template, session, redirect, request

from site_web import site_blueprint
from site_web.flask_site import api_address


@site_blueprint.route('/admin/')
def admin():
    return redirect('booking')


@site_blueprint.route('/admin/booking')
def bookings():
    bookings_data = requests.get(f"{api_address}/api/booking",  headers=session['auth'])
    return render_template('admin/booking-history.html', bookings_data=bookings_data.json())



@site_blueprint.route('/admin/booking/<int:id>')
def booking_detail(id):
    if request.method == 'GET':
        booking_data = requests.get(f"{api_address}/api/booking/{id}",  headers=session['auth'])
        booking = json.loads(booking_data.json())
        return render_template('admin/booking-detail.html', booking=booking)
    elif request.method == 'POST':
        data = request.get_json()
