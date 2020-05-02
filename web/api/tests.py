from unittest import TestCase
from flask import Flask

from models import db, Person, PersonType


class DatabaseTest(TestCase):

    def setUp(self) -> None:
        app = Flask(__name__)

        HOST = "35.228.215.119"
        USER = "root"
        PASSWORD = "carshare"
        DATABASE = "carshare_db_test"

        app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        db.init_app(app)
        self.app = app
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def test_add_person_to_db(self):
        person_type = PersonType(
            id=1,
            type='Customer'
        )
        person = Person(
            id=1,
            username='test',
            first_name='first',
            last_name='last',
            email='test@gmail.com',
            person_type=1,
            password_hashed='password',
            face=None
        )
        with self.app.app_context():
            db.session.add(person_type)
            db.session.commit()
            db.session.add(person)
            db.session.commit()
            p = Person.query.filter_by(username='test').first()
            print(p)
            self.assertEqual(p.username, 'test')