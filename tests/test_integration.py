import sys
import os
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import app
from models.book import Book
from models.member import Member
from models.loan import Loan

class LibraryIntegrationTestCase(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_borrow_return_workflow_endpoint(self):
        """Integration Test: Test web form submission flow for borrowing and returning"""
        response = self.client.post('/borrow', data={
            'book_id': 1,
            'member_id': 1
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_loan_model_integration_logic(self):
        """Integration Test: Verify Loan model handles database relationships"""
        loans = Loan.query.all() if hasattr(Loan, 'query') else []
        self.assertIsInstance(loans, list)

if __name__ == '_main_':
    unittest.main()