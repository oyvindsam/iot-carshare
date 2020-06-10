from unittest import TestCase

import carshare_config_local
from api.test.populate_db import populate_db
from app import create_app


def get_test_app():
    app = create_app(carshare_config_local.DevelopmentConfig)
    with app.app_context():
        populate_db(app)
    return app

def get_credentials(app):
    with app.app_context():
        with app.test_client() as app:
            data = {
                'username': 'as',
                'password': 'as'
            }
            response = app.post('api/auth/login', json=data)
            return response.get_json()


class BookingTest(TestCase):
    def setUp(self) -> None:
        self.app = get_test_app()
        login_data = get_credentials(self.app)
        self.header = {'Authorization': 'Bearer ' + login_data['access_token']}
        self.username = login_data['username']
        self.person_id = login_data['person_id']

    def test_booking_page(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                response = app.get('bookcar', headers=self.header)
                self.assertTrue(200, response.status_code)


class LoginTest(TestCase):
    def setUp(self) -> None:
        self.app = get_test_app()

    def test_login(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                data = {
                    'username': 'username',
                    'password': 'password'
                }
                response = app.post('/login', data=data)




