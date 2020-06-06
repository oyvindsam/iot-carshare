import base64

import PIL
import requests
from flask import render_template

from site_web import site_blueprint
from site_web.flask_site import api_address
from site_web.site_login import require_type


@site_blueprint.route('/manager')
@require_type(['MANAGER', 'ADMIN'])
def manger():
    response = requests.get(f"{api_address}/api/manager/statistics/car-usage")
    data = response.json()
    img_path = data['car-usage-url']
    return render_template('manager.html', car_usage=img_path)