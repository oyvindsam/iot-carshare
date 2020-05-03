import json
from datetime import datetime, timedelta

from api.models import PersonType, Person, Car, CarManufacturer, CarType, \
    CarColour, Booking


class DummyPerson:

    p1 = Person(
        username='test',
        first_name='first',
        last_name='last',
        email='test@gmail.com',
        person_type=1,
        password_hashed='password',
        face=None
    )

    p2 = Person(
        username='test2',
        first_name='first2',
        last_name='last2',
        email='test2@gmail.com',
        person_type=1,
        password_hashed='password',
        face=None
    )

    p1_json = json.dumps({
        'id': 1,
        'username': 'test',
        'first_name': 'first',
        'last_name': 'last',
        'email': 'test@gmail.com',
        'person_type': 1,
        'password_hashed': 'password',
    })

    p2_json_no_id = json.dumps({
        'username': 'test2',
        'first_name': 'first2',
        'last_name': 'last2',
        'email': 'test2@gmail.com',
        'person_type': 1,
        'password_hashed': 'password',
    })


class DummyPersonType:
    pt1 = PersonType(
        id=1,
        type='Customer'
    )

    pt1_json = json.dumps({
        'id': 1,
        'type': 'Customer'
    })


class DummyCar:
    c1 = Car(
        reg_number='abc123',
        car_manufacturer=1,
        car_type=1,
        seats=4,
        latitude='59.9139',
        longitude='10.7522',
        hour_rate=20.5,
    )


class DummyCarManufacturer:
    cm1 = CarManufacturer(
        manufacturer='BMW'
    )


class DummyCarType:
    ct1 = CarType(
        type='Suv'
    )


class DummyCarColour:
    cc = CarColour(
        colour='White'
    )


class DummyBooking:
    b1 = Booking(
        car_id=1,
        person_id=1,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=5),
        booking_status=1
    )

    b1_no_id_json = json.dumps({
        'car_id': 1,
        'person_id': 1,
        'start_time': '2020-05-03T21:2',
        'end_time': '2020-05-04T02:2',
        'booking_status': 1
    })