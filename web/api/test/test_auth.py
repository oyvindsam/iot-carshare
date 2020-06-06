from unittest import TestCase

from werkzeug.security import generate_password_hash

from api.models import PersonSchema
from api.test.dummy_data import *
from api.test.tests import get_test_app, add_to_db


class ApiAuthTest(TestCase):
    def setUp(self) -> None:
        self.app = get_test_app()

        with self.app.app_context():
            # set up persons
            person1 = DummyPerson.create_random()
            person2 = DummyPerson.create_random()
            self.person1_password = person1.password_hashed # save password for later use
            self.person1_data = {
                'username': person1.username,
                'password': person1.password_hashed  # note: this is the unhased password
            }
            person1.password_hashed = generate_password_hash(person1.password_hashed)
            person2.password_hashed = generate_password_hash(person2.password_hashed)

            self.person1 = add_to_db(person1).id
            self.person2 = add_to_db(person2).id

            with self.app.test_client() as app:
                response = app.post('api/auth/login', json=self.person1_data)
                self.person1_token = response.get_json().get('access_token')

    def test_register_user(self):
        with self.app.test_client() as app:
            person1 = DummyPerson.create_random()
            person_json = PersonSchema(exclude=['id', 'person_type']).dumps(person1)

            response = app.post('api/auth/register', json=person_json)
            self.assertEqual(201, response.status_code)
            new_person = Person.query.filter_by(username=person1.username).first()
            self.assertNotEqual(person1.password_hashed, new_person.password_hashed)

    def test_registered_user_can_log_in(self):
        with self.app.test_client() as app:

            person = Person.query.get(self.person1)

            response = app.post('api/auth/login', json=self.person1_data)
            self.assertTrue('access_token' in response.get_json())

    def test_registered_user_can_access_protected_endpoint(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                person = Person.query.get(self.person1)

                response = app.get(f"api/person/{person.username}", headers={
                    'Authorization': 'Bearer ' + self.person1_token})
                self.assertEqual(200, response.status_code)

    def test_registered_customer_user_cannot_access_another_users_endpoint(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                person = Person.query.get(self.person1)
                person2 = Person.query.get(self.person2)

                response = app.get(f"api/person/{person2.username}", headers={
                    'Authorization': 'Bearer ' + self.person1_token})
                self.assertEqual(403, response.status_code)

