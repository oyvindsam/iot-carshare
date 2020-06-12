import requests
from flask import render_template, session

from site_web import site_blueprint
from site_web.flask_site import api_address
from site_web.site_login import require_type


@site_blueprint.route('/engineer')
@require_type(['ENGINEER', 'ADMIN'])
def engineer():
    """
    Load cars from api and pass to car list view
    Returns: view

    """
    car_data = requests.get(f"{api_address}/api/engineer/car",
                            headers=session['auth'])
    return render_template('engineer.html', car_data=car_data.json())