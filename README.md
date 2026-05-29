# IT6 Final Drill: REST API Enhancement (Sakila Integration)

# Implemented API Endpoints
- **GET** - Retrieve or get the information of the customers up to 50 active customer records like their ID's.
                @app.route("/customers", methods=["GET"])
                def get_customers():
                    data = data_fetch("Select customer_id, first_name, last_name, email, active FROM customer LIMIT 50")
                    return make_response(jsonify(data), 200)
  
- **GET** - Retrieves specific customer profile tracking.
                @app.route("/customers/<int:id>", methods=["GET"])
                def get_customer_by_id(id):
                    data = data_fetch("SELECT customer_id, first_name, last_name, email, active FROM customer where customer_id = %s", (id,))
                    if not data:
                        return make_response(jsonify({"message": "customer not found"}), 404)
                    return make_response(jsonify(data), 200)
- **POST**  - Validates payload data and appends a new customer.
                @app.route("/customers", methods=["POST"])
                def add_customer():
                    info = request.get_json()
                    if not info or not all(k in info for k in ("first_name", "last_name", "address_id")):
                        return make_response(jsonify({"error": "Bad request: Missing required fields"}), 400)
                    
                    current = mysql.connection.cursor()
                    current.execute(
                        """ INSERT INTO customer (first_name, last_name, address_id) VALUE (%s, %s, %s)""",
                        (info["first_name"], info["last_name"], info["address_id"]),
                    )
                    mysql.connection.commit()
                    new_id = current.lastrowid
                    current.close()
                    return make_response(jsonify({"message": "customer added successfully", "customer_id": new_id}), 201)

- **PUT** - Modifies profile parameter layers.
                @app.route("/customers/<int:id>", methods=["PUT"])
                def update_customer(id):
                    info = request.get_json()
                    if not info or not all(k in info for k in ("first_name", "last_name", "email")):
                        return make_response(jsonify({"error": "Bad request: Missing payload items"}), 400)
                    
                    existing_data = data_fetch("SELECT customer_id FROM customer WHERE customer_id = %s", (id,))
                    if not existing_data:
                        return make_response(jsonify({"message": "customer not found"}), 404)
                    
                    current = mysql.connection.cursor()
                    current.execute(
                        """ UPDATE customer SET first_name = %s, last_name = %s, email = %s WHERE customer_id = %s """,
                        (info["first_name"], info["last_name"], info["email"], id),
                    )
                    mysql.connection.commit()
                    current.close()
                    return make_response(jsonify({"message": "customer updated successfully"}), 200)

- **DELETE** - Removes a record or gracefully soft-deletes (sets `active=0`) if foreign key constraints block a physical drop action.
              @app.route("/customers/<int:id>", methods=["DELETE"])
              def delete_customer(id):
                  existing_data = data_fetch("SELECT customer_id FROM customer WHERE customer_id = %s", (id,))
                  if not existing_data:
                      return make_response(jsonify({"message": "customer not found"}), 404)
                  
                  current = mysql.connection.cursor()
                  try:
                      current.execute("DELETE FROM customer where customer_id = %s", (id,))
                      mysql.connection.commit()
                  except Exception as e:
                      current.execute("UPDATE customer SET active = 0 WHERE customer_id = %s", (id,))
                      mysql.connection.commit()
              
                  current.close()
                  return make_response(jsonify({"message": "customer deleted successfully"}), 200)
- **GET/POST/PUT/DELETE** `/actors` - Complete CRUD lifecycle management for system actors.

# Display CRUD (Create, Remove, Update, Delete) on the terminal
It desplay the CRUD methods using test.py 
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
# Testing Approach
- Unit tests were written using Python's `unittest` framework paired with `unittest.mock.patch` to guarantee complete layer isolation. Database operations are completely mocked (`MagicMock`) to evaluate route logic without altering physical records.
- To test or run: `python -m unittest tests.py`
