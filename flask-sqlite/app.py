from flask import Flask, request, jsonify
from models import db, Student

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def home():
    return jsonify({"message": "Flask Student API"}), 200

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([
        {"id": s.id, "name": s.name, "age": s.age} for s in students
    ])

@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    
    # Validation
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    if 'name' not in data or not isinstance(data['name'], str) or not data['name'].strip():
        return jsonify({"error": "Invalid or missing 'name'"}), 400
    if 'age' not in data or not isinstance(data['age'], int):
        return jsonify({"error": "Invalid or missing 'age'"}), 400

    student = Student(name=data['name'].strip(), age=data['age'])
    db.session.add(student)
    db.session.commit()
    return jsonify({"id": student.id}), 201

@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()

    # Validation
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name'].strip():
            return jsonify({"error": "Invalid 'name'"}), 400
        student.name = data['name'].strip()
    if 'age' in data:
        if not isinstance(data['age'], int):
            return jsonify({"error": "Invalid 'age'"}), 400
        student.age = data['age']

    db.session.commit()
    return jsonify({"message": "Updated"}), 200

@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
