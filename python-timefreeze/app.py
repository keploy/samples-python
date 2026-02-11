from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
# It's good practice to load this from environment variables in a real application
app.config["SECRET_KEY"] = "unsafe_secret" 

# In-memory storage to remove the database dependency for simplicity
users = {}
items = {}
next_item_id = 1

# JWT token decorator to protect routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            # Expecting token format: "Bearer <token>"
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Malformed token header!'}), 400

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token to validate it and get the user's identity
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # Check if the user from the token exists in our store
            if data['username'] not in users:
                 return jsonify({'message': 'User from token not found!'}), 401
            current_user = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        
        # Pass the current user's username to the decorated function
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login_user():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify, missing username or password'}), 401

    username = auth['username']
    user_password_hash = users.get(username)

    if not user_password_hash:
        return jsonify({'message': 'User not found'}), 401

    if check_password_hash(user_password_hash, auth['password']):
        # Create a token with a 2-minute expiration time
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token})

    return jsonify({'message': 'Password is wrong'}), 403

# --- CRUD Operations for a simple "item" resource ---

@app.route('/item', methods=['POST'])
@token_required
def add_item(current_user):
    global next_item_id
    data = request.json
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    item_id_str = str(next_item_id)
    # Store item data associated with the user who created it
    items[item_id_str] = {'data': data, 'owner': current_user}
    next_item_id += 1
    
    # Return the ID of the newly created item
    return jsonify({'message': 'Item added', 'id': item_id_str}), 201

@app.route('/item/<id>', methods=['GET'])
@token_required
def get_item(current_user, id):
    item = items.get(id)
    if item:
        # For simplicity, any authenticated user can view any item.
        return jsonify(item['data']), 200
    else:
        return jsonify({'message': 'Item not found'}), 404

@app.route('/item/<id>', methods=['PUT'])
@token_required
def update_item(current_user, id):
    data = request.json
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    
    if id in items:
        # Simple authorization: only the owner can update their own item
        if items[id]['owner'] != current_user:
            return jsonify({'message': 'Permission denied: you are not the owner'}), 403
        items[id]['data'].update(data)
        return jsonify({'message': 'Item updated'}), 200
    else:
        return jsonify({'message': 'Item not found'}), 404

@app.route('/item/<id>', methods=['DELETE'])
@token_required
def delete_item(current_user, id):
    if id in items:
        # Simple authorization: only the owner can delete their own item
        if items[id]['owner'] != current_user:
            return jsonify({'message': 'Permission denied: you are not the owner'}), 403
        del items[id]
        return jsonify({'message': 'Item deleted'}), 200
    else:
        return jsonify({'message': 'Item not found'}), 404

# --- User Management ---

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    if username in users:
        return jsonify({'message': 'User already exists'}), 409

    hashed_password = generate_password_hash(password)
    users[username] = hashed_password

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/user/delete/<username>', methods=['DELETE'])
@token_required
def delete_user_by_username(current_user, username):
    # Simple authorization: a user can only delete their own account
    if current_user != username:
        return jsonify({'message': 'Permission denied: you can only delete your own account'}), 403

    if username in users:
        del users[username]
        # Clean up items owned by the deleted user
        items_to_delete = [item_id for item_id, item in items.items() if item['owner'] == username]
        for item_id in items_to_delete:
            del items[item_id]
        return jsonify({'message': 'User and their items deleted successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    # Binds to all network interfaces, making it accessible for testing
    app.run(host='0.0.0.0', port=5000, debug=False)
