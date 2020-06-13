import requests
from flask import render_template

from site_web import site_blueprint
from site_web.flask_site import api_address
from site_web.site_login import require_type


@site_blueprint.route('/manager')
@require_type(['MANAGER', 'ADMIN'])
def manger():
    response_car_usage = requests.get(f"{api_address}/api/manager/statistics/car-usage")
    data_car_usage = response_car_usage.json()
    car_usage = data_car_usage['car-usage-url']

    response_week_active = requests.get(
        f"{api_address}/api/manager/statistics/week-active")
    data_week_active = response_week_active.json()
    week_active = data_week_active['week-active-url']

    images = {
        'car_usage': car_usage,
        'week_active': week_active
    }
    print(images)
    return render_template('manager.html', images=images)