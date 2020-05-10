import json
from datetime import datetime, timedelta
from uuid import uuid4

from api.models import PersonType, Person, Car, CarManufacturer, CarType, \
    CarColour, Booking, BookingStatus


class DummyPersonType:
    customer = PersonType(
        type='Customer'
    )

    @staticmethod
    def create_random():
        return PersonType(
            type=uuid4().__str__()[:50]
        )

    pt_customer_no_id_json = json.dumps({
        'type': 'Customer'
    })


class DummyPerson:
    person_customer1 = Person(
        username='test',
        first_name='first',
        last_name='last',
        email='test@gmail.com',
        person_type=1,
        password_hashed='password',
        face=None
    )

    person_customer2 = Person(
        username='test2',
        first_name='first2',
        last_name='last2',
        email='test2@gmail.com',
        person_type=1,
        password_hashed='password',
        face=None
    )

    @staticmethod
    def create_random() -> Person:
        return Person(
            username=uuid4().__str__()[:50],
            first_name='random',
            last_name='random',
            email='random@gmail.com',
            person_type=1,
            password_hashed='password',
            face=None
        )

    def creat_random_json(id: int =None):
        if id is None:
            return json.dumps({
                'username': uuid4().__str__()[:50],
                'first_name': 'first',
                'last_name': 'last',
                'email': 'test@gmail.com',
                'person_type': 1,
                'password_hashed': 'password',
            })

        return json.dumps({
            'id': id,
            'username': uuid4().__str__()[:50],
            'first_name': 'first',
            'last_name': 'last',
            'email': 'test@gmail.com',
            'person_type': 1,
            'password_hashed': 'password',
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


class DummyBookingStatus:
    available = BookingStatus(
        status='Available'
    )

    not_available = BookingStatus(
        status='Not available'
    )

    @staticmethod
    def create_random():
        return BookingStatus(
            status=uuid4().__str__()[:20]
        )


class DummyBooking:
    person1_car1_available = Booking(
        car_id=1,
        person_id=1,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=5),
        status_id=1
    )

    @staticmethod
    def create_random():
        return Booking(
            car_id=1,
            person_id=1,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=5),
            status_id=1
        )



    b1_json = json.dumps({
        'car_id': 1,
        'person_id': 1,
        'start_time': '2020-05-03T21:2',
        'end_time': '2020-05-04T02:2',
        'status_id': 1
    })

    b1_id_json = json.dumps({
        'id': 1,
        'car_id': 1,
        'person_id': 1,
        'start_time': '2020-05-03T21:2',
        'end_time': '2020-05-04T02:2',
        'status_id': 1
    })
