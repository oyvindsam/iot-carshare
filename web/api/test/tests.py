from unittest import TestCase
from flask import Flask

from api.api import api
from api.models import db
from api.test.dummy_data import *


def get_test_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:?cache=shared'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)
    app.register_blueprint(api)
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app


class DatabaseTest(TestCase):

    def setUp(self) -> None:
        self.app = get_test_app()


    def test_add_person_to_db(self):
        with self.app.app_context():
            db.session.add(DummyPersonType.c1)
            db.session.commit()
            db.session.add(DummyPerson.p1)
            db.session.commit()
            db.session.add(DummyPerson.p2)
            db.session.commit()
            p1 = Person.query.filter_by(username=DummyPerson.p1.username).first()
            p2 = Person.query.filter_by(username=DummyPerson.p2.username).first()
            print(p1, p2)
            self.assertEqual(p1.username, DummyPerson.p1.username)
            self.assertTrue(p1.id < p2.id)


class ApiTest(TestCase):

    def setUp(self) -> None:
        self.app = get_test_app()

    def test_add_person(self):
        with self.app.test_client() as app:
            response = app.post('/api/person_type', json=DummyPersonType.c1_json)
            print(response.status_code)