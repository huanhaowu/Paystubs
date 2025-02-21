import unittest
from datetime import datetime
from lib.generate_pdf import generate_pdf

class GeneratePDFTestCase(unittest.TestCase):
    def test_generate_pdf(self):
        pdf_content = generate_pdf(
            full_name='John Doe',
            email='john.doe@example.com',
            position='Developer',
            health_discount_amount=50.0,
            social_discount_amount=30.0,
            taxes_discount_amount=20.0,
            other_discount_amount=10.0,
            gross_salary=1000.0,
            gross_payment=900.0,
            net_payment=800.0,
            period=datetime.strptime('2025-02-21', '%Y-%m-%d'),
            company_name='ATDEv',
            country='do'
        )
        self.assertIsNotNone(pdf_content)
        self.assertIsInstance(pdf_content, bytes)

if __name__ == '__main__':
    unittest.main()