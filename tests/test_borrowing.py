import sys
import os
import unittest

# Idinadagdag nito ang main folder sa path ng Python para laging mahanap ang app at models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models.book import Book
from member import Member
from loan import Loan

class LibraryTestCase(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_01_index_route(self):
        """Test 1: Check if index page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_02_add_book_get(self):
        """Test 2: Check if add book page loads"""
        response = self.client.get('/add-book')
        self.assertEqual(response.status_code, 200)

    def test_03_add_member_get(self):
        """Test 3: Check if add member page loads"""
        response = self.client.get('/add-member')
        self.assertEqual(response.status_code, 200)

    def test_04_borrow_route_missing_data(self):
        """Test 4: Borrowing without data handles failure/redirect"""
        response = self.client.post('/borrow', data={}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_05_book_model_structure(self):
        """Test 5: Verify Book model has required methods"""
        self.assertTrue(hasattr(Book, 'get_all_books'))
        self.assertTrue(hasattr(Book, 'add_book'))

    def test_06_member_model_structure(self):
        """Test 6: Verify Member model has required methods"""
        self.assertTrue(hasattr(Member, 'get_all_members'))
        self.assertTrue(hasattr(Member, 'add_member'))

    def test_07_loan_model_structure(self):
        """Test 7: Verify Loan model has required borrowing method"""
        self.assertTrue(hasattr(Loan, 'borrow_book'))

    def test_08_app_secret_key(self):
        """Test 8: Verify Flask app configuration secret key exists"""
        self.assertIsNotNone(app.secret_key)

if __name__ == '_main_':
    unittest.main()

