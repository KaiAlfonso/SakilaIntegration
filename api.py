from flask import Flask, make_response, jsonify, request
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config.from_pyfile("config.py") 

mysql = MySQL(app)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


def data_fetch(query, params=None):
    cur = mysql.connection.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data


@app.route("/actors", methods=["GET"])
def get_actors():
    data = data_fetch("""select * from actor""")
    return make_response(jsonify(data), 200)


@app.route("/actors/<int:id>", methods=["GET"])
def get_actor_by_id(id):
    data = data_fetch("""SELECT * FROM actor where actor_id = %s""", (id,))
    return make_response(jsonify(data), 200)


@app.route("/actors/<int:id>/movies", methods=["GET"])
def get_movies_by_actor(id):
    data = data_fetch(
        """
        SELECT film.title, film.release_year 
        FROM actor 
        INNER JOIN film_actor
        ON actor.actor_id = film_actor.actor_id 
        INNER JOIN film
        ON film_actor.film_id = film.film_id 
        WHERE actor.actor_id = %s
    """, (id,))
    return make_response(
        jsonify({"actor_id": id, "count": len(data), "movies": data}), 200
    )


@app.route("/actors", methods=["POST"])
def add_actor():
    cur = mysql.connection.cursor()
    info = request.get_json()
    first_name = info["first_name"]
    last_name = info["last_name"]
    cur.execute(
        """ INSERT INTO actor (first_name, last_name) VALUE (%s, %s)""",
        (first_name, last_name),
    )
    mysql.connection.commit()
    print("row(s) affected :{}".format(cur.rowcount))
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "actor added successfully", "rows_affected": rows_affected}
        ),
        201,
    )


@app.route("/actors/<int:id>", methods=["PUT"])
def update_actor(id):
    cur = mysql.connection.cursor()
    info = request.get_json()
    first_name = info["first_name"]
    last_name = info["last_name"]
    cur.execute(
        """ UPDATE actor SET first_name = %s, last_name = %s WHERE actor_id = %s """,
        (first_name, last_name, id),
    )
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "actor updated successfully", "rows_affected": rows_affected}
        ),
        200,
    )


@app.route("/actors/<int:id>", methods=["DELETE"])
def delete_actor(id):
    cur = mysql.connection.cursor()
    cur.execute(""" DELETE FROM actor where actor_id = %s """, (id,))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()
    return make_response(
        jsonify(
            {"message": "actor deleted successfully", "rows_affected": rows_affected}
        ),
        200,
    )


@app.route("/actors/format", methods=["GET"])
def get_params():
    fmt = request.args.get("id")
    foo = request.args.get("aaaa")
    return make_response(jsonify({"format": fmt, "foo": foo}), 200)


@app.route("/customers", methods=["GET"])
def get_customers():
    data = data_fetch("Select customer_id, first_name, last_name, email, active FROM customer LIMIT 50")
    return make_response(jsonify(data), 200)


@app.route("/customers/<int:id>", methods=["GET"])
def get_customer_by_id(id):
    data = data_fetch("SELECT customer_id, first_name, last_name, email, active FROM customer where customer_id = %s", (id,))
    if not data:
        return make_response(jsonify({"message": "customer not found"}), 404)
    return make_response(jsonify(data), 200)

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

@app.route("/actors/format", methods=["GET"])
def get_parameter():
    fmt = request.args.get("id")
    foo = request.args.get("aaaa")
    return make_response(jsonify({"format": fmt, "foo": foo}), 200)

if __name__ == "__main__":
    app.run(debug=True)