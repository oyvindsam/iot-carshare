from unittest import TestCase
from flask import Flask

from api.models import db, Person, PersonType
from api.test.dummy_data import DummyPerson, DummyPersonType


class DatabaseTest(TestCase):

    def setUp(self) -> None:
        self.app = Flask(__name__)
        HOST = "35.228.215.119"
        USER = "root"
        PASSWORD = "carshare"
        DATABASE = "carshare_db_test"
        self.app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(self.app)
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def test_add_person_to_db(self):

        with self.app.app_context():
            db.session.add(DummyPersonType.c1)
            db.session.commit()
            db.session.add(DummyPerson.p1)
            db.session.add(DummyPerson.p2)
            db.session.commit()
            p1 = Person.query.filter_by(username=DummyPerson.p1.username).first()
            p2 = Person.query.filter_by(username=DummyPerson.p2.username).first()
            self.assertEqual(p1.username, DummyPerson.p1.username)
            self.assertTrue(p1.id < p2.id)


