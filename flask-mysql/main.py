import os
from flask import Flask, jsonify, request
from flask.json.provider import JSONProvider
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import json
import mysql.connector
import sys
import decimal
import time

# --- Custom JSON Provider to Handle Datetime and Decimal ---
class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, default=self.default)
    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)
    @staticmethod
    def default(o):
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        if isinstance(o, decimal.Decimal):
            return str(o)
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

app = Flask(__name__)
app.json = CustomJSONProvider(app)

# --- App Configuration ---
app.config["JWT_SECRET_KEY"] = "super-secret-key-for-testing"
jwt = JWTManager(app)

# --- User Authentication ---
users = {"admin": {"username": "admin", "password": generate_password_hash("admin123")}}

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not (user := users.get(username)) or not check_password_hash(user["password"], password):
        return jsonify({"msg": "Bad username or password"}), 401
    return jsonify(access_token=create_access_token(identity=username))

# --- Database Configuration & Connection ---
DB_CFG = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER", "demo"),
    password=os.getenv("DB_PASSWORD", "demopass"),
    database=os.getenv("DB_NAME", "demo"),
)

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CFG)
    except mysql.connector.Error as err:
        print(f"FATAL: Could not connect to database: {err}", file=sys.stderr)
        return None

def setup_database():
    """Creates/resets and populates the database tables on startup."""
    print("Connecting to database to run setup...")
    conn = get_db_connection()
    if not conn: sys.exit(1)
    
    try:
        print("Setting up tables...")
        cur = conn.cursor()
        
        # Disable FK checks and drop tables
        cur.execute("SET foreign_key_checks = 0;")
        cur.execute("DROP TABLE IF EXISTS transactions, api_logs, accounts, token_blacklist_blacklistedtoken, token_blacklist_outstandingtoken, django_migrations, permissions, clients, payloads, programs;")
        cur.execute("SET foreign_key_checks = 1;")
        
        # Rest of your setup code...
        conn.commit()
        
    except mysql.connector.Error as err:
        print(f"Database setup failed: {err}")
        conn.rollback()
        sys.exit(1)
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()
    print("Database setup complete.")
    """Creates/resets and populates the database tables on startup."""
    print("Connecting to database to run setup...")
    conn = get_db_connection()
    if not conn: sys.exit(1)
    
    try:
        print("Setting up tables...")
        cur = conn.cursor()
        
        # Disable FK checks and drop tables
        cur.execute("SET foreign_key_checks = 0;")
        cur.execute("DROP TABLE IF EXISTS transactions, api_logs, accounts, token_blacklist_blacklistedtoken, token_blacklist_outstandingtoken, django_migrations, permissions, clients, payloads, programs;")
        cur.execute("SET foreign_key_checks = 1;")
        
        # Rest of your setup code...
        conn.commit()
        
    except mysql.connector.Error as err:
        print(f"Database setup failed: {err}")
        conn.rollback()
        sys.exit(1)
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()
    print("Database setup complete.")
    """Creates/resets and populates the database tables on startup."""
    print("Connecting to database to run setup...")
    conn = get_db_connection()
    if not conn: sys.exit(1)
    
    print("Setting up tables...")
    cur = conn.cursor()
    
    cur.execute("SET foreign_key_checks = 0;")
    cur.execute("DROP TABLE IF EXISTS transactions, api_logs, accounts, token_blacklist_blacklistedtoken, token_blacklist_outstandingtoken, django_migrations, permissions, clients, payloads, programs;")
    cur.execute("SET foreign_key_checks = 1;")
    
    # Create tables
    cur.execute("CREATE TABLE programs (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100));")
    cur.execute("CREATE TABLE clients (id BIGINT PRIMARY KEY AUTO_INCREMENT, display_name VARCHAR(255) NOT NULL, client_status VARCHAR(50), program_id INT NULL, FOREIGN KEY (program_id) REFERENCES programs(id));")
    cur.execute("CREATE TABLE accounts (id BIGINT PRIMARY KEY AUTO_INCREMENT, client_id BIGINT, account_no_dataphile VARCHAR(100) NULL, market_value DECIMAL(20, 2), FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE);")
    cur.execute("CREATE TABLE transactions (id BIGINT PRIMARY KEY AUTO_INCREMENT, from_account_id BIGINT, to_account_id BIGINT, amount DECIMAL(20, 2), transaction_time TIMESTAMP, FOREIGN KEY (from_account_id) REFERENCES accounts(id), FOREIGN KEY (to_account_id) REFERENCES accounts(id));")
    cur.execute("CREATE TABLE permissions (id BIGINT PRIMARY KEY AUTO_INCREMENT, role_name VARCHAR(100), resource_name VARCHAR(100), can_read BOOLEAN);")
    cur.execute("CREATE TABLE payloads (id BIGINT PRIMARY KEY AUTO_INCREMENT, data LONGTEXT);")
    cur.execute("CREATE TABLE django_migrations (id INT AUTO_INCREMENT PRIMARY KEY, app VARCHAR(255) NOT NULL, name VARCHAR(255) NOT NULL, applied DATETIME NOT NULL);")
    cur.execute("CREATE TABLE token_blacklist_outstandingtoken (id INT AUTO_INCREMENT PRIMARY KEY, jti VARCHAR(255) UNIQUE NOT NULL, token TEXT NOT NULL, created_at DATETIME, expires_at DATETIME NOT NULL);")
    cur.execute("CREATE TABLE token_blacklist_blacklistedtoken (id INT AUTO_INCREMENT PRIMARY KEY, token_id INT NOT NULL, blacklisted_at DATETIME NOT NULL, FOREIGN KEY (token_id) REFERENCES token_blacklist_outstandingtoken(id));")
    cur.execute("CREATE TABLE api_logs (id INT AUTO_INCREMENT PRIMARY KEY, timestamp DATETIME, endpoint VARCHAR(255), method VARCHAR(10), request_headers TEXT, request_body TEXT, response_code INT, response_body TEXT, user_agent VARCHAR(255), ip_address VARCHAR(45), duration_ms INT, status VARCHAR(20), correlation_id VARCHAR(100), service_name VARCHAR(100), log_level VARCHAR(20), error_message TEXT);")

    # Insert sample data
    cur.execute("INSERT INTO programs (name) VALUES ('Premium'), ('Standard'), ('Legacy');")
    cur.execute("INSERT INTO clients (display_name, client_status, program_id) VALUES ('Global Corp Inc.', 'Active', 1), ('Tech Innovators LLC', 'Active', 1), ('Legacy Systems', 'Inactive', 3), ('Solo Trader', 'Active', 2);")
    cur.execute("INSERT INTO accounts (client_id, account_no_dataphile, market_value) VALUES (1, 'F12345', 150000.75), (1, 'F12346', 25000.50), (2, 'F54321', 75000.00), (4, 'F98765', 12000.00);")
    cur.execute("INSERT INTO django_migrations (app, name, applied) VALUES ('contenttypes', '0001_initial', NOW()), ('auth', '0001_initial', NOW());")
    cur.execute("INSERT INTO token_blacklist_outstandingtoken (jti, token, expires_at) VALUES ('9522d59c56404995af98d4c30bde72b3', 'dummy-token', NOW() + INTERVAL 1 DAY);")
    cur.execute("INSERT INTO token_blacklist_blacklistedtoken (token_id, blacklisted_at) VALUES (1, NOW());")
    cur.execute("INSERT INTO permissions (role_name, resource_name, can_read) VALUES ('admin', 'ClientsViewSet', true);")

    conn.commit()
    cur.close()
    conn.close()
    print("Database setup complete.")

# --- Health Check ---
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

# --- Original Simple Endpoints ---
@app.route("/data", methods=["POST"])
@jwt_required()
def create_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO payloads (data) VALUES (%s)", (request.json.get("message"),))
    conn.commit()
    conn.close()
    return jsonify({"status": "created"}), 201

@app.route("/data", methods=["GET"])
@jwt_required()
def get_all_data():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, data FROM payloads ORDER BY id DESC")
    payloads = cur.fetchall()
    conn.close()
    return jsonify(payloads)

# --- Initial Complex Endpoint ---
@app.route("/generate-complex-queries", methods=["GET"])
@jwt_required()
def generate_complex_queries():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    results = {}
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT c.id as client_id, c.display_name, a.id as account_id, a.account_no_dataphile FROM clients c INNER JOIN accounts a ON c.id = a.client_id WHERE c.id = 1")
        results['join_query'] = cur.fetchall()
        cur.execute("SELECT id, display_name FROM clients WHERE id IN (SELECT client_id FROM accounts WHERE market_value > 50000)")
        results['subquery_query'] = cur.fetchall()
        cur.execute("SELECT role_name FROM permissions WHERE can_read = TRUE")
        results['permission_query'] = cur.fetchall()
        return jsonify(results)
    finally:
        if conn and conn.is_connected(): conn.close()

# --- Second Set of Complex Endpoints ---
@app.route("/system/status", methods=["GET"])
@jwt_required()
def get_system_status():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT VERSION() AS version, @@sql_mode AS sql_mode, @@default_storage_engine AS storage_engine, CONVERT_TZ('2001-01-01 01:00:00', 'UTC', 'UTC') IS NOT NULL AS utc_check")
        return jsonify(cur.fetchone())
    finally:
        if conn and conn.is_connected(): conn.close()

@app.route("/system/migrations", methods=["GET"])
@jwt_required()
def get_migrations():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT `id`, `app`, `name`, `applied` FROM `django_migrations`")
        return jsonify(cur.fetchall())
    finally:
        if conn and conn.is_connected(): conn.close()

@app.route("/auth/check-token/<string:jti>", methods=["GET"])
@jwt_required()
def check_blacklisted_token(jti):
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cur = conn.cursor(dictionary=True)
        query = "SELECT 1 AS `is_blacklisted` FROM `token_blacklist_blacklistedtoken` bt INNER JOIN `token_blacklist_outstandingtoken` ot ON (bt.`token_id` = ot.`id`) WHERE ot.`jti` = %s LIMIT 1"
        cur.execute(query, (jti,))
        return jsonify({"status": "Token is blacklisted" if cur.fetchone() else "Token is valid"})
    finally:
        if conn and conn.is_connected(): conn.close()

@app.route("/logs", methods=["POST"])
@jwt_required()
def create_api_log():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cur = conn.cursor()
        query = "INSERT INTO `api_logs` (`timestamp`, `endpoint`, `method`, `request_headers`, `request_body`, `response_code`, `response_body`, `user_agent`, `ip_address`, `duration_ms`, `status`, `correlation_id`, `service_name`, `log_level`, `error_message`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        params = (datetime.datetime.now(), request.path, request.method, json.dumps(dict(request.headers)), json.dumps(request.json), 201, '{"status": "logged"}', request.user_agent.string, request.remote_addr, 55, 'SUCCESS', request.headers.get("X-Request-ID", "N/A"), 'api-logger', 'INFO', None)
        cur.execute(query, params)
        conn.commit()
        return jsonify({"status": "log created", "id": cur.lastrowid}), 201
    finally:
        if conn and conn.is_connected(): conn.close()

@app.route("/reports/client-summary", methods=["GET"])
@jwt_required()
def generate_client_summary():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("DROP TEMPORARY TABLE IF EXISTS client_summary;")
        cursor.execute("CREATE TEMPORARY TABLE `client_summary` (client_id INT, total_balance DECIMAL(20,2));")
        cursor.execute("INSERT INTO `client_summary` (client_id, total_balance) SELECT client_id, SUM(market_value) FROM accounts GROUP BY client_id;")
        cursor.execute("SELECT c.display_name, cs.total_balance FROM `client_summary` cs JOIN clients c ON cs.client_id = c.id ORDER BY cs.total_balance DESC;")
        return jsonify(cursor.fetchall())
    finally:
        if conn and conn.is_connected(): conn.close()
        


# --- Most Complex Endpoints ---
@app.route("/reports/full-financial-summary", methods=["GET"])
@jwt_required()
def get_full_financial_summary():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cur = conn.cursor(dictionary=True)
        query = """
            SELECT c.display_name, p.name AS program_name,
                   (SELECT COUNT(*) FROM accounts a2 WHERE a2.client_id = c.id) AS number_of_accounts,
                   SUM(a.market_value) AS total_market_value,
                   CASE WHEN SUM(a.market_value) > 100000 THEN 'Tier 1'
                        WHEN SUM(a.market_value) BETWEEN 50000 AND 100000 THEN 'Tier 2'
                        ELSE 'Tier 3'
                   END AS client_tier
            FROM clients c
            LEFT JOIN accounts a ON c.id = a.client_id
            LEFT JOIN programs p ON c.program_id = p.id
            WHERE c.client_status = 'Active'
            GROUP BY c.id, p.name
            HAVING total_market_value > 10000 OR number_of_accounts > 0
            ORDER BY total_market_value DESC;
        """
        cur.execute(query)
        return jsonify(cur.fetchall())
    finally:
        if conn and conn.is_connected(): conn.close()

@app.route("/search/clients", methods=["GET"])
@jwt_required()
def search_clients():
    search_term = request.args.get('q', '')
    if not search_term: return jsonify({"error": "Query parameter 'q' is required."}), 400
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cur = conn.cursor(dictionary=True)
        query = "SELECT DISTINCT c.id, c.display_name, c.client_status FROM clients c JOIN (SELECT id, client_id, account_no_dataphile FROM accounts) AS a ON c.id = a.client_id WHERE (c.display_name LIKE %s OR a.account_no_dataphile LIKE %s);"
        like_pattern = f"%{search_term}%"
        cur.execute(query, (like_pattern, like_pattern))
        return jsonify(cur.fetchall())
    finally:
        if conn and conn.is_connected(): conn.close()

@app.route("/transactions/transfer", methods=["POST"])
@jwt_required()
def transfer_funds():
    data = request.json
    from_id, to_id, amount = data.get('from_account_id'), data.get('to_account_id'), decimal.Decimal(data.get('amount', 0))
    if not all([from_id, to_id, amount > 0]): return jsonify({"error": "Missing or invalid parameters"}), 400
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cur = conn.cursor(dictionary=True)
        conn.start_transaction()
        cur.execute("SELECT market_value FROM accounts WHERE id = %s FOR UPDATE", (from_id,))
        from_account = cur.fetchone()
        if not from_account or from_account['market_value'] < amount:
            conn.rollback()
            return jsonify({"error": "Insufficient funds"}), 400
        cur.execute("UPDATE accounts SET market_value = market_value - %s WHERE id = %s", (amount, from_id))
        cur.execute("UPDATE accounts SET market_value = market_value + %s WHERE id = %s", (amount, to_id))
        cur.execute("INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_time) VALUES (%s, %s, %s, %s)", (from_id, to_id, amount, datetime.datetime.now()))
        conn.commit()
        return jsonify({"status": "Transfer successful"}), 200
    except mysql.connector.Error as err:
        if conn.is_connected(): conn.rollback()
        return jsonify({"error": f"Transaction failed: {err}"}), 500
    finally:
        if conn and conn.is_connected(): conn.close()

if __name__ == "__main__":
    setup_database()
    app.run(host="0.0.0.0", port=5000)