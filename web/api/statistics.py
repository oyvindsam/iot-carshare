import base64
import os
from io import BytesIO

import matplotlib.pyplot as plt
from flask import send_file, send_from_directory

from api import api_blueprint
from api.models import Booking


def get_folder():
    path = 'site_web/static/api/resource/statistics'
    if not os.path.exists(path):
        os.makedirs(path)
    return path


@api_blueprint.route('/manager/statistics/car-usage', methods=['GET'])
def car_usage():
    bookings = Booking.query.all()
    times = []
    for booking in bookings:
        time = (booking.end_time - booking.start_time)
        hours = time.days * 24 + time.seconds // 3600
        times.append(hours)

    plt.hist(times, bins=10)
    plt.title('Hours booked')
    plt.xlabel('Hours')
    plt.ylabel('Frequency')

    # FIXME: This is supposed to be saved on the API filesystem, then the
    # url to the image is returned when requesting this endpoint.
    # Not it is saving it in the website's static folder path, this is horrible
    folder = get_folder()

    file_name = 'car-usage-latest.jpg'
    path = f"{folder}/{file_name}"
    plt.savefig(path)
    web_path = path.split('site_web')[1]
    return {'car-usage-url': web_path}
