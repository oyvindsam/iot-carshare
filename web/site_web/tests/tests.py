from unittest import TestCase

import carshare_config_local
from app import create_app


def get_test_app():
    app = create_app(carshare_config_local.DevelopmentConfig)
    return app


class LoginTest(TestCase):
    def setUp(self) -> None:
        self.app = get_test_app()

    def test_login(self):
        with self.app.app_context():
            with self.app.test_client() as app:
                response = app.post('login', data={'username': '1'})

