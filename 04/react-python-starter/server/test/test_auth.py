import json
from test.base import BaseTestCase
from app.api.models.user import User
from app import db

class TestAuth(BaseTestCase):
    def test_registration(self):
        """Ensure a new user can be added to the database."""
        with self.client:
            response = self.client.post(
                '/register',
                data=json.dumps({
                    'username': 'testuser',
                    'email': 'testuser@email.com',
                    'password': 'password123'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertTrue(data['auth_token'])
            self.assertEqual(data['message'], 'Successfully registered.')

    def test_login(self):
        """Ensure a user can log in."""
        with self.client:
            # Register user
            self.client.post(
                '/register',
                data=json.dumps({
                    'username': 'logintest',
                    'email': 'login@email.com',
                    'password': 'password123'
                }),
                content_type='application/json'
            )
            # Login user
            response = self.client.post(
                '/login',
                data=json.dumps({
                    'email': 'login@email.com',
                    'password': 'password123'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
