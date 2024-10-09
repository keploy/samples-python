from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flaskuser:password@db:5432/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __init__(self, name):
        self.name = name

# Create the database tables
@app.before_first_request
def create_tables():
    db.create_all()

# Home route
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the User Management API!"}), 200

# GET all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name} for user in users])

# POST a new user
@app.route('/users', methods=['POST'])
def add_user():
    name = request.json.get('name')
    if not name:
        return jsonify({"error": "Name is required."}), 400
    user = User(name=name)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": f"User {name} added.", "id": user.id}), 201


# PUT to update a user
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({"error": "User not found."}), 404
    
    name = request.json.get('name')
    if name:
        user.name = name
        db.session.commit()
        return jsonify({"message": f"User {id} updated."})
    
    return jsonify({"error": "Name is required."}), 400

# DELETE a user
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({"error": "User not found."}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {id} deleted."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
