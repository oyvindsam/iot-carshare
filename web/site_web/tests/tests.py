from unittest import TestCase

import carshare_config_local
from api.test.populate_db import populate_db
from app import create_app


def get_test_app():
    app = create_app(carshare_config_local.DevelopmentConfig)
    with app.app_context():
        populate_db(app)
    return app


def get_credentials(app, username, password):
    with app.app_context():
        with app.test_client() as app:
            data = {
                'username': username,
                'password': password
            }
            app.post('/login', data=data)


class AdminPageTest(TestCase):
    def setUp(self) -> None:
        self.app = get_test_app()
        self.username = 'admin'
        self.password = 'admin'
        get_credentials(self.app, self.username, 'admin')

    def test_admin_page(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                data = {
                    'username': 'admin',
                    'password': 'admin'
                }
                reponse = app.post('/login', data=data)
                response = app.get('/admin')
                self.assertTrue(200, response.status_code)


class BookingTest(TestCase):
    def setUp(self) -> None:
        self.app = get_test_app()

    def login(self):
        get_credentials(self.app, 'as', 'as')

    def test_booking_page(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                self.login()  # does not persist auth session
                response = app.get('bookcar')
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




