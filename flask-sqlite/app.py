from flask import Flask, request, jsonify
from models import db, Student

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 🔧 Validation Helper Function
def validate_student_data(data, partial=False):
    if not data:
        return "Missing JSON body"

    if not partial:
        if 'name' not in data:
            return "Missing 'name'"
        if 'age' not in data:
            return "Missing 'age'"

    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name'].strip():
            return "Invalid 'name'"

    if 'age' in data:
        if not isinstance(data['age'], int):
            return "Invalid 'age'"

    return None  # No error

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
    error = validate_student_data(data)
    if error:
        return jsonify({"error": error}), 400

    student = Student(name=data['name'].strip(), age=data['age'])
    db.session.add(student)
    db.session.commit()
    return jsonify({"id": student.id}), 201

@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()
    error = validate_student_data(data, partial=True)
    if error:
        return jsonify({"error": error}), 400

    if 'name' in data:
        student.name = data['name'].strip()
    if 'age' in data:
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
