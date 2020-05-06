from unittest import TestCase

from flask import Flask
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from api.api import api
from api.models import db, PersonSchema, BookingSchema
from api.test.dummy_data import *


def get_test_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:?cache=shared'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)
    app.register_blueprint(api)
    with app.app_context():
        db.create_all()
    return app


class DatabaseTest(TestCase):

    def setUp(self) -> None:
        self.app = get_test_app()

    def test_add_person_to_db(self):
        with self.app.app_context():
            db.session.add(DummyPerson.p1)
            db.session.add(DummyPerson.p2)
            db.session.commit()
            p1 = Person.query.filter_by(username=DummyPerson.p1.username).first()
            p2 = Person.query.filter_by(username=DummyPerson.p2.username).first()
            self.assertEqual(p1.username, DummyPerson.p1.username)
            self.assertTrue(p1.id < p2.id)


class ApiTest(TestCase):

    def setUp(self) -> None:
        self.app = get_test_app()

    def test_add_person_type(self):
        with self.app.test_client() as app:
            response = app.post('/api/person_type', json=DummyPersonType.pt1_json)
            self.assertEqual(response.status_code, 201)

    # id is automatically added by the db
    def test_cant_add_person_with_id(self):
        with self.app.test_client() as app:
            response_post = app.post('/api/person', json=DummyPerson.p1_id_json)
            self.assertEqual(response_post.status_code, 409)


    def test_add_get_person(self):
        with self.app.test_client() as app:

            response_post = app.post('/api/person', json=DummyPerson.p1_no_id_json)
            self.assertEqual(response_post.status_code, 201)

            response_get = app.get(f'/api/person/{DummyPerson.p1.username}')
            self.assertEqual(response_get.status_code, 200)

    def test_add_invalid_person_raises_error(self):
        with self.app.test_client() as app:
            # empty first_name among other missing fields
            invalid_person = json.dumps({'username': 'valid', 'first_name': ''})
            with self.assertRaises(ValidationError) as cm:
                app.post('/api/person', json=invalid_person)
            self.assertTrue('first_name' in cm.exception.messages)

    def test_add_two_persons_with_same_id_raises_error(self):
        with self.app.test_client() as app:
            response_post = app.post('/api/person', json=DummyPerson.p1_no_id_json)
            self.assertEqual(response_post.status_code, 201)
            with self.assertRaises(IntegrityError) as cm:
                response = app.post('/api/person', json=DummyPerson.p1_no_id_json)

    def test_add_booking(self):
        with self.app.test_client() as app:
            response_post = app.post('/api/booking', json=DummyBooking.b1_json)
            self.assertEqual(response_post.status_code, 201)

    # id is automatically added by the db
    def test_cant_add_booking_with_id(self):
        with self.app.test_client() as app:
            response_post = app.post('/api/booking', json=DummyBooking.b1_id_json)
            self.assertEqual(response_post.status_code, 409)

    def test_get_booking(self):
        with self.app.test_client() as app:
            response_post = app.post('/api/booking', json=DummyBooking.b1_json)
            self.assertEqual(response_post.status_code, 201)
            username = DummyPerson.p1.username



class ModelTest(TestCase):
    def setUp(self) -> None:
        self.app = get_test_app()

        # TODO: set up valid references in dummy data?


    # for now, only test data that might actually be used by the api for first assignment
    def test_schema_load_data_from_json(self):
        with self.app.app_context():
            person_schema = PersonSchema()
            person = person_schema.loads(DummyPerson.p2_json_no_id)
            self.assertEqual(type(person), Person)

            booking_schema = BookingSchema()
            # deserialize to json string
            booking_json = booking_schema.dumps(DummyBooking.b1)
            # serialize from json string
            booking = booking_schema.loads(DummyBooking.b1_json)
            self.assertEqual(type(booking), Booking)

    def test_person_type_relationship(self):
        p1 = DummyPerson.create_random()
        p2 = DummyPerson.create_random()
        pt1 = DummyPersonType.pt1
        p1.person_type = pt1.id
        p2.person_type = pt1.id
        with self.app.app_context():
            db.session.add(pt1)
            db.session.add(p1)
            db.session.add(p2)
            db.session.commit()

            self.assertEqual(Person.query.filter_by(username=p1.username).first().type.id, pt1.id)
            self.assertEqual(Person.query.filter_by(username=p2.username).first().type.id, pt1.id)
            # check that person1 and person2 are in the list of persons backreferenced from personType
            self.assertTrue(set([p1, p2]) <= set(PersonType.query.filter_by(id=pt1.id).first().person))

    def test_car_relationships(self):
        ct = DummyCarType.ct1
        manu = DummyCarManufacturer.cm1
        with self.app.app_context():
            db.session.add(ct)
            db.session.add(manu)
            db.session.commit()
            print(id)
            # now retrieve and get id given by db
            ct = CarType.query.filter_by(type=ct.type).first()
            manu = CarManufacturer.query.filter_by(manufacturer=manu.manufacturer).first()

        # be sure id point to valid type/manufacturer
        car = DummyCar.c1
        car.car_type = ct.id
        car.car_manufacturer = manu.id

        with self.app.app_context():
            db.session.add(car)
            db.session.commit()

            # check references to/from car/carType/carManufacturer
            self.assertEqual(Car.query.filter_by(reg_number=car.reg_number).first().type.id, ct.id)
            self.assertEqual(Car.query.filter_by(reg_number=car.reg_number).first().manufacturer.id, manu.id)
            self.assertTrue(set([car]) <= set(CarManufacturer.query.filter_by(manufacturer=manu.manufacturer).first().car))
            self.assertTrue(set([car]) <= set(CarType.query.filter_by(type=ct.type).first().car))






