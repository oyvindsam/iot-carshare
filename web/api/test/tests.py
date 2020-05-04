from unittest import TestCase
from flask import Flask

from api.api import api
from api.models import db, PersonSchema, PersonTypeSchema, BookingSchema
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

    def test_add_get_person(self):
        with self.app.test_client() as app:

            response_post = app.post('/api/person', json=DummyPerson.p1_json)
            self.assertEqual(response_post.status_code, 201)

            response_get = app.get(f'/api/person/{DummyPerson.p1.username}')
            self.assertEqual(response_get.status_code, 200)


class ModelTest(TestCase):
    def setUp(self) -> None:
        self.app = get_test_app()

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


