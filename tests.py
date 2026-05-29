import unittest
import json
import warnings
from unittest.mock import MagicMock, patch
from api import app

class MyAppTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()
        warnings.simplefilter("ignore", category=DeprecationWarning)

    def test_index_page(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "<p>Hello, World!</p>")

    @patch('api.mysql')
    def test_getactors(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"actor_id": 1, "first_name": "PENELOPE", "last_name": "GUINESS"},
        ]
        mock_mysql.connection.cursor.return_value = mock_cursor

        response = self.app.get("/actors")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("PENELOPE" in response.data.decode())

    @patch('api.mysql')
    def test_getactors_by_id(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"actor_id": 88, "first_name": "JOE", "last_name": "PESCI"},
        ]
        mock_mysql.connection.cursor.return_value = mock_cursor

        response = self.app.get("/actors/88")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("PESCI" in response.data.decode())

    @patch('api.mysql')
    def test_get_customers_success(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"customer_id": 1, "first_name": "MARY", "last_name": "SMITH", "email": "mary@test.com", "active": 1}
        ]
        mock_mysql.connection.cursor.return_value = mock_cursor

        response = self.app.get("/customers")
        self.assertEqual(response.status_code, 200)
        self.assertIn("MARY", response.data.decode())

    @patch('api.mysql')
    def test_get_customers_id_success(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"customer_id": 1, "first_name": "MARY", "last_name": "SMITH", "email": "mary@test.com", "active": 1}
        ]
        mock_mysql.connection.cursor.return_value = mock_cursor

        response = self.app.get("/customers/1")        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data[0]["first_name"], "MARY")

    @patch('api.mysql')
    def test_get_customers_id_not_found(self, mock_mysql):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_mysql.connection.cursor.return_value = mock_cursor

        response = self.app.get("/customers/999")        
        self.assertEqual(response.status_code, 404)
        self.assertIn("customer not found", response.data.decode())

    @patch('api.mysql')
    def test_add_customer_success(self, mock_mysql):
        """Positive Test: Create valid entry."""
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 600
        mock_mysql.connection.cursor.return_value = mock_cursor

        payload = {
            "store_id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "address_id": 5,
            "email": "johndoe@test.com"
        }
        response = self.app.post("/customers", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("customer added successfully", response.data.decode())

    @patch('api.mysql')
    def test_add_customer_bad_request(self, mock_mysql):
        """Negative Test: Payload elements completely missing."""
        payload = {"first_name": "Broken Payload"} 
        response = self.app.post("/customers", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Bad request", response.data.decode())

    @patch('api.mysql')
    def test_update_customer_success(self, mock_mysql):
        """Positive Test: Modify profile parameters successfully."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"customer_id": 1}]
        mock_mysql.connection.cursor.return_value = mock_cursor

        payload = {"first_name": "Jane", "last_name": "Smith", "email": "janesmith@test.com"}
        response = self.app.put("/customers/1", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("customer updated successfully", response.data.decode())

    @patch('api.mysql')
    def test_delete_customer_not_found(self, mock_mysql):
        """Negative Test: Drop entity transaction targets missing entry."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_mysql.connection.cursor.return_value = mock_cursor

        response = self.app.delete("/customers/777")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()