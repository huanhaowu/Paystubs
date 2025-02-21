import unittest
from unittest.mock import patch, Mock
import pandas as pd
from lib.send_email import send_payroll_email

class SendEmailTestCase(unittest.TestCase):
    @patch('lib.send_email.smtplib.SMTP')
    @patch('lib.send_email.generate_pdf')
    def test_send_payroll_email(self, mock_generate_pdf, mock_smtp):
        data = {
            'full_name': ['John Doe'],
            'email': ['john.doe@example.com'],
            'position': ['Developer'],
            'health_discount_amount': [50.0],
            'social_discount_amount': [30.0],
            'taxes_discount_amount': [20.0],
            'other_discount_amount': [10.0],
            'gross_salary': [1000.0],
            'gross_payment': [900.0],
            'net_payment': [800.0],
            'period': ['2025-02-21']
        }
        df = pd.DataFrame(data)

        # Convert the period field to datetime
        df['period'] = pd.to_datetime(df['period'])

        mock_generate_pdf.return_value = b'PDF content'
        mock_server = Mock()
        mock_smtp.return_value = mock_server

        email_results = send_payroll_email(df, 'do', 'ATDEv')
        self.assertEqual(len(email_results), 1)
        self.assertEqual(email_results[0]['status'], 'success')


if __name__ == '__main__':
    unittest.main()