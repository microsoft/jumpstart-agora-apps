import unittest
from unittest.mock import MagicMock, patch, Mock
from flask import Flask, session, request
from app import app, get_cursor, cart, add_to_cart, checkout

class TestApp(unittest.TestCase):
    def setUp(self):
        self.mock_conn = patch.object(app, 'conn', return_value=None)
        app.testing = True
        self.client = app.test_client()

    @patch('psycopg2.connect')
    def test_get_cursor(self, mock_connect):      
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        cursor = get_cursor()
        mock_connect.return_value.cursor.assert_called_once()
        self.assertEqual(cursor, mock_cursor)
      
    @patch('flask.session', {'cart': [{'id': '1', 'name': 'Product 1', 'price': 10.0, 'quantity': 1}]})
    def test_cart(self):        
        response = self.client.get('/cart')
        self.assertIsNotNone(response)    
            
    @patch('app.get_cursor')
    @patch('flask.session', {'cart': []})
    def test_checkout_with_empty_cart(self, mock_cursor):
        response = self.client.get('/checkout')
        assert response.status == '302 FOUND'

if __name__ == '__main__':
    unittest.main()
