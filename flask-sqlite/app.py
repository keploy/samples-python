from flask import Flask, request, jsonify
from models import db, Student
from werkzeug.exceptions import HTTPException
import logging
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///students.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret_key')
db.init_app(app)

# Config Logging
logging.basicConfig(level=logging.INFO)

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
        if len(data['name'].strip()) > 100:
            return "'name' too long"
    if 'age' in data:
        if not isinstance(data['age'], int):
            return "Invalid 'age'"
        if data['age'] < 0 or data['age'] > 150:
            return "'age' out of valid range"
    return None  # No error

# Test Route
@app.route('/')
def home():
    return jsonify({"success": True, "message": "Flask Student API"}), 200

# CRUD Routes
# Get all students
@app.route('/students', methods=['GET'])
def get_students():
    try:
        page = int(request.args.get('page',1))
        per_page = int(request.args.get('per_page',10))
    except ValueError:
        return jsonify({"success":False, "error":"'page' and 'per_page' must be integers"}), 400

    students = Student.query.all()


# Filtering by name partial match
    name_filter = request.args.get('name')
    if name_filter:
        students_query = students_query.filter(Student.name.ilike(f'%{name_filter}%'))

# Filtering by age exact match
    age_filter = request.args.get('age')
    if age_filter and age_filter.isdigit():
        students_query = students_query.filter(Student.age == int(age_filter))

    pagination = students_query.paginate(page=page, per_page=per_page, error_out=False)
    students = pagination.items

    return jsonify({
        "success": True,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "total_pages": pagination.pages,
        "students":[
            {"id": s.id, "name": s.name, "age": s.age} for s in students
    ]}), 200

# Add a new student
@app.route('/students', methods=['POST'])
def add_student():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    error = validate_student_data(data)
    if error:
        return jsonify({"success": False, "error": error}), 400
    student = Student(name=data['name'].strip(), age=data['age'])
    db.session.add(student)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"DB Error: {e}")
        return jsonify({"success": False, "error": "Database error"}), 500
    return jsonify({"success": True, "id": student.id, "name": student.name}), 201

# Update a student
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({"success": False, "error": "Student not found"}), 404
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400
    error = validate_student_data(data, partial=True)
    if error:
        return jsonify({"success": False, "error": error}), 400
    if 'name' in data:
        student.name = data['name'].strip()
    if 'age' in data:
        student.age = data['age']
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"DB Error: {e}")
        return jsonify({"success": False, "error": "Database error"}), 500
    return jsonify({"success": True, "message": "Updated"}), 200

# Delete a student
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({"success": False, "error": "Student not found"}), 404
    try:
        db.session.delete(student)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"DB Error: {e}")
        return jsonify({"success": False, "error": "Database error"}), 500
    return jsonify({"success": True, "message": "Deleted"}), 200

# Global Exception Handler
@app.errorhandler(Exception)
def handle_exception(e):
    # Handle HTTP errors
    if isinstance(e, HTTPException):
        return jsonify({"success": False, "error": str(e)}), e.code
    logging.error(f"Unhandled Error: {e}")
    return jsonify({"success": False, "error": "Internal server error"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run() # Remove debug=True for production
