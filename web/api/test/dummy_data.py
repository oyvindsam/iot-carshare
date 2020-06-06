import json
from datetime import datetime, timedelta
from uuid import uuid4

from werkzeug.security import generate_password_hash

from api.models import PersonType, Person, Car, CarManufacturer, CarType, \
    CarColour, Booking, BookingStatusEnum


class DummyPerson:
    person_customer1 = Person(
        username='test',
        first_name='first',
        last_name='last',
        email='test@gmail.com',
        type=PersonType.CUSTOMER,
        password=generate_password_hash('password'),
        face=None
    )

    person_customer2 = Person(
        username='test2',
        first_name='first2',
        last_name='last2',
        email='test2@gmail.com',
        type=PersonType.CUSTOMER,
        password=generate_password_hash('password'),
        face=None
    )

    @staticmethod
    def create_random() -> Person:
        return Person(
            username=uuid4().__str__()[:50],
            first_name='random',
            last_name='random',
            email='random@gmail.com',
            type=PersonType.CUSTOMER,
            password=generate_password_hash('password'),
            face=None
        )

    def create_random_json(id: int =None):
        if id is None:
            return json.dumps({
                'username': uuid4().__str__()[:50],
                'first_name': 'first',
                'last_name': 'last',
                'email': 'test@gmail.com',
                'type': 'CUSTOMER',
                'password': generate_password_hash('password'),
                'face': None
            })

        return json.dumps({
            'id': id,
            'username': uuid4().__str__()[:50],
            'first_name': 'first',
            'last_name': 'last',
            'email': 'test@gmail.com',
            'type': 'CUSTOMER',
            'password': generate_password_hash('password'),
        })


class DummyCarManufacturer:
    bmw = CarManufacturer(
        manufacturer='BMW'
    )

    @staticmethod
    def create_random():
        return CarManufacturer(
            manufacturer=uuid4().__str__()[:20]
        )


class DummyCarType:
    suv = CarType(
        type='Suv'
    )

    @staticmethod
    def create_random():
        return CarType(
            type=uuid4().__str__()[:20]
        )


class DummyCarColour:
    white = CarColour(
        colour='White'
    )

    @staticmethod
    def create_random():
        return CarColour(
            colour=uuid4().__str__()[:20]
        )


class DummyCar:
    bmw_suv_white = Car(
        reg_number='abc123',
        car_manufacturer=1,
        car_type=1,
        car_colour=1,
        seats=4,
        latitude='59.9139',
        longitude='10.7522',
        hour_rate=20.5,
    )

    @staticmethod
    def create_random():
        return  Car(
            reg_number=uuid4().__str__()[:6],
            car_manufacturer=1,
            car_type=1,
            car_colour=1,
            seats=4,
            latitude='59.9139',
            longitude='10.7522',
            hour_rate=20.5,
        )

class DummyBooking:
    person1_car1_available = Booking(
        car_id=1,
        person_id=1,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=5),
    )

    @staticmethod
    def create_random():
        return Booking(
            car_id=1,
            person_id=1,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=5),
        )



    b1_json = json.dumps({
        'car_id': 1,
        'person_id': 1,
        'start_time': '2020-05-03T21:2',
        'end_time': '2020-05-04T02:2',
    })

    b1_id_json = json.dumps({
        'id': 1,
        'car_id': 1,
        'person_id': 1,
        'start_time': '2020-05-03T21:2',
        'end_time': '2020-05-04T02:2',
    })
