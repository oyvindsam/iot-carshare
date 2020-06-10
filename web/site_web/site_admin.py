import requests
from flask import render_template, session

from site_web import site_blueprint
from site_web.flask_site import api_address


@site_blueprint.route('/admin')
def admin():
    booking_data = requests.get(f"{api_address}/api/booking",  headers=session['auth'])
    return render_template('admin/booking-history.html', booking_data=booking_data.json())