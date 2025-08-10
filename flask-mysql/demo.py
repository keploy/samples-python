from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
import mysql.connector
import time

app = Flask(__name__)

# --- JWT and User Setup (Unchanged) ---
app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=1000000)
jwt = JWTManager(app)

users = {
    "admin": {"username": "admin", "password": generate_password_hash("admin123"), "role": "admin"},
    "user": {"username": "user", "password": generate_password_hash("user123"), "role": "user"}
}

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Flask JWT API!"})

@app.route("/login", methods=["POST"])
def login():
    if not request.is_json: return jsonify({"msg": "Missing JSON in request"}), 400
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password: return jsonify({"msg": "Missing username or password"}), 400
    user = users.get(username, None)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=username)
    return jsonify({"access_token": access_token, "user": {"username": user["username"], "role": user["role"]}}), 200

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    user = users.get(current_user)
    return jsonify({"message": f"Hello, {current_user}!", "user": user}), 200

# --- Database Connection and Setup (Unchanged) ---
DB_CFG = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER", "demo"),
    password=os.getenv("DB_PASSWORD", "demopass"),
    database=os.getenv("DB_NAME", "demo"),
)

while True:
    try:
        conn = mysql.connector.connect(**DB_CFG)
        cur = conn.cursor(buffered=True)
        break
    except mysql.connector.Error:
        time.sleep(1)

cur.execute("""
CREATE TABLE IF NOT EXISTS products (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(255) NOT NULL,
    quantity    INT,
    price       DECIMAL(10, 2),
    description BLOB,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
conn.commit()

# --- NEW: Endpoints for Robustly Testing MySQL Protocol ---

@app.route("/robust-test/create", methods=["POST"])
@jwt_required()
def robust_create_product():
    """
    This endpoint tests a query with multiple parameters of different types.
    It will trigger the following parts of the MySQL protocol:
    - if CLIENT_QUERY_ATTRIBUTES is set { ... }
    - parameter_count > 0 (it will be 4)
    - new_params_bind_flag will be set
    - A loop for each parameter to send its `param_type_and_flag`
    - `parameter_values` will contain the binary representation of the data.
    """
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON body"}), 400

    name = data.get("name")
    quantity = data.get("quantity")
    price = data.get("price")
    # This description can contain any characters, including null bytes.
    # The library handles encoding it safely.
    description = data.get("description", "")

    if not name or quantity is None or price is None:
        return jsonify({"msg": "Missing required fields: name, quantity, price"}), 400
    
    # This is the SAFE and CORRECT way to execute a parameterized query.
    # The library handles creating the packet structure from the diagram.
    sql = "INSERT INTO products (name, quantity, price, description) VALUES (%s, %s, %s, %s)"
    params = (name, quantity, price, description)
    
    cur.execute(sql, params)
    conn.commit()
    
    new_id = cur.lastrowid
    
    return jsonify({
        "status": "created",
        "id": new_id,
        "message": f"Product '{name}' created successfully."
    }), 201

@app.route("/robust-test/create-with-null", methods=["POST"])
@jwt_required()
def robust_create_with_null():
    """
    This endpoint specifically tests the handling of NULL values.
    It will trigger the `null_bitmap` field in the protocol packet.
    The `null_bitmap` will have a bit set to 1 for the 'price' and 
    'description' parameters, indicating they are NULL.
    """
    data = request.get_json()
    if not data or "name" not in data or "quantity" not in data:
        return jsonify({"msg": "Missing required fields: name, quantity"}), 400

    name = data.get("name")
    quantity = data.get("quantity")
    
    # We are explicitly setting price and description to None.
    # The connector will translate this to SQL NULL.
    sql = "INSERT INTO products (name, quantity, price, description) VALUES (%s, %s, %s, %s)"
    params = (name, quantity, None, None) # Using Python's None
    
    cur.execute(sql, params)
    conn.commit()
    
    new_id = cur.lastrowid
    
    return jsonify({
        "status": "created_with_null",
        "id": new_id,
        "message": f"Product '{name}' created with NULL price and description."
    }), 201

@app.route("/robust-test/get-all", methods=["GET"])
@jwt_required()
def robust_get_all_products():
    """Reads all product entries to verify the inserts."""
    cur.execute("SELECT id, name, quantity, price, description, created_at FROM products ORDER BY id DESC")
    rows = cur.fetchall()
    
    # Handle BLOB data which might be bytes
    def convert_row(row_tuple, columns):
        row_dict = dict(zip(columns, row_tuple))
        if 'description' in row_dict and isinstance(row_dict['description'], bytes):
            # Attempt to decode as UTF-8, fall back to a safe representation
            try:
                row_dict['description'] = row_dict['description'].decode('utf-8')
            except UnicodeDecodeError:
                row_dict['description'] = repr(row_dict['description'])
        return row_dict

    columns = [col[0] for col in cur.description]
    products = [convert_row(row, columns) for row in rows]
    return jsonify(products)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)