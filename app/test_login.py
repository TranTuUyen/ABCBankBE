
import json
from bson.json_util import dumps
from unittest import TestCase
from app import app


class TestLogin(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_login(self):
        # Mock data
        mock_login_data = {
            'email': 'admin@gmail.com',
            'password': '12345678'
        }

        # Set expected result
        user = {
            '_id': {'$oid': '5cd8235200b8bd0a20d1061e'},
            'role': 'Admin',
            'email': 'admin@gmail.com',
        }
        page_sanitized = json.loads(dumps(user))
        expected_json = json.loads(dumps({'ok': True, 'data': page_sanitized}))

        # Get actual result
        response = self.app.post('/api/v1/login', json=mock_login_data)
        actual_result = json.loads(response.get_data(as_text=True))
        actual_body = actual_result['data']

        # Compare expected result and actual actual result
        self.assertTrue(actual_body['token'])
        self.assertTrue(actual_body['refresh'])
        del actual_result['data']['token']
        del actual_result['data']['refresh']
        self.assertDictEqual(actual_result, expected_json)

    def test_login_nojson_request(self):
        # Get actual result
        response = self.app.post('/api/v1/login', json=None)
        self.assertEquals(response._status_code, 400)

    def test_login_noemail_request(self):
        # Mock data
        mock_login_data = {
            'password': '12345678'
        }

        # Get actual result
        response = self.app.post('/api/v1/login', json=mock_login_data)
        self.assertEquals(response._status_code, 400)

    def test_login_nopassword_request(self):
        # Mock data
        mock_login_data = {
            'email': 'admin@gmail.com'
        }

        # Get actual result
        response = self.app.post('/api/v1/login', json=mock_login_data)
        self.assertEquals(response._status_code, 400)

    def test_login_wrong_email_request(self):
        # Mock data
        mock_login_data = {
            'email': 'wrongemail@gmail.com',
            'password': '12345678'
        }

        # Get actual result
        response = self.app.post('/api/v1/login', json=mock_login_data)
        self.assertEquals(response._status_code, 400)

    def test_login_wrong_email_request(self):
        # Mock data
        mock_login_data = {
            'email': 'admin@gmail.com',
            'password': 'wrongpassword'
        }

        # Get actual result
        response = self.app.post('/api/v1/login', json=mock_login_data)
        self.assertEquals(response._status_code, 400)
