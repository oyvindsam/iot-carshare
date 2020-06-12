import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt

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

    fig, ax = plt.subplots()

    plt.hist(times, bins=10)
    plt.title('Hours booked frequency')
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


@api_blueprint.route('/manager/statistics/week-active', methods=['GET'])
def get_last_week_active():
    bookings = filter(
        lambda b: (b.start_time > datetime.now() - timedelta(weeks=1)) &
                  (b.start_time < datetime.now()),
        Booking.query.all())
    bookings = [b for b in bookings]
    xs = [datetime.now().replace(hour=0, minute=0) - timedelta(days=x) for x in
          range(7, 0, -1)]  # hours in a week
    ys = []
    for day in xs:
        day_count = 0
        end = day + timedelta(days=1)

        for b in bookings:
            print(b.start_time)
            if (b.start_time < day < b.end_time) \
                    | (day < b.start_time < end) \
                    | (day < b.start_time < end):
                day_count += 1
        ys.append(day_count)

    xs = [x.strftime('%d-%m-%y') for x in xs]

    fig, ax = plt.subplots()

    plt.plot(xs, ys)
    plt.xlabel('Date')
    plt.ylabel('Active rentals')
    plt.title('Active rentals per day for last 7 days')
    # FIXME: This is supposed to be saved on the API filesystem, then the
    # url to the image is returned when requesting this endpoint.
    # Not it is saving it in the website's static folder path, this is horrible
    folder = get_folder()

    file_name = 'week-active-latest.jpg'
    path = f"{folder}/{file_name}"
    plt.savefig(path)
    web_path = path.split('site_web')[1]
    return {'week-active-url': web_path}
