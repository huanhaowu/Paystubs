import os
import unittest
from unittest.mock import patch, Mock
from app import app, users
from werkzeug.security import generate_password_hash
from base64 import b64encode
from io import BytesIO
import pandas as pd

class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.username = os.getenv('AUTH_USERNAME')
        self.password = os.getenv('AUTH_PASSWORD')
        self.hashed_password = generate_password_hash(self.password)
        users[self.username] = self.hashed_password

    def tearDown(self):
        pass

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"Welcome to the paystubs - assessment")

    def test_upload_file_no_file(self):
        auth_header = {
            'Authorization': 'Basic ' + b64encode(f"{self.username}:{self.password}".encode('utf-8')).decode(
                'utf-8')
        }
        response = self.app.post('/upload', headers=auth_header, data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"No file part", response.data)

    def test_upload_file_invalid_file_format(self):
        auth_header = {
            'Authorization': 'Basic ' + b64encode(f"{self.username}:{self.password}".encode('utf-8')).decode(
                'utf-8')
        }
        data = {
            'file': (BytesIO(b"fake content"), 'test.txt')
        }
        response = self.app.post('/upload', headers=auth_header, content_type='multipart/form-data', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid file format, only .csv files are allowed", response.data)

    @patch('app.send_payroll_email')
    @patch('app.pd.read_csv')
    def test_upload_file_valid(self, mock_read_csv, mock_send_payroll_email):
        auth_header = {
            'Authorization': 'Basic ' + b64encode(f"{self.username}:{self.password}".encode('utf-8')).decode(
                'utf-8')
        }
        csv_content = (
            "full_name,email,position,health_discount_amount,social_discount_amount,"
            "taxes_discount_amount,other_discount_amount,gross_salary,gross_payment,net_payment,period\n"
            "John Doe,huanhaowu28@gmail.com,Manager,200.00,150.00,300.00,50.00,5000.00,5200.00,4500.00,2025-01-01\n"
        )
        data = {
            'file': (BytesIO(csv_content.encode('utf-8')), 'test.csv'),
            'country': 'do',
            'company': 'ATDEv'
        }
        # Create a mock DataFrame
        df_data = {
            'full_name': ['John Doe'],
            'email': ['huanhaowu28@gmail.com'],
            'position': ['Manager'],
            'health_discount_amount': [200.0],
            'social_discount_amount': [150.0],
            'taxes_discount_amount': [300.0],
            'other_discount_amount': [50.0],
            'gross_salary': [5000.0],
            'gross_payment': [5200.0],
            'net_payment': [4500.0],
            'period': [pd.to_datetime('2025-01-01')]
        }
        mock_df = pd.DataFrame(df_data)

        mock_read_csv.return_value = mock_df
        mock_send_payroll_email.return_value = []

        response = self.app.post('/upload', headers=auth_header, content_type='multipart/form-data', data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"email_results", response.data)

if __name__ == '__main__':
    unittest.main()