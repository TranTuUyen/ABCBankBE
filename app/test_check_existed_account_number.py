
import json
from bson.json_util import dumps
from unittest import TestCase
from app import app


class TestCheckExistedAccountNumber(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_check_account_number(self):
        mock_account_number = {
            'account_number': 1001
        }
        response = self.app.post('/api/v1/accounts/check_account_number', json=mock_account_number)
        self.assertEquals(response._status_code, 409)

    def test_check_account_number_not_exist(self):
        mock_account_number = 100008
        response = self.app.post('/api/v1/accounts/check_account_number', json=mock_account_number)
        self.assertEqual(response.status_code, 200)
