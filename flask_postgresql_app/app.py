from flask import Flask, request, jsonify, abort
from pymongo import MongoClient
from flask_cors import CORS
from bson.objectid import ObjectId
from bson.errors import InvalidId
import os
from werkzeug.exceptions import HTTPException

app = Flask(_name_)

# Config from environment variables
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'studentsdb')

# Secure CORS (adjust in production)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
students_collection = db['students']
students_collection.create_index('student_id', unique=True)  # Prevent duplicates

@app.errorhandler(HTTPException)
def handle_error(e):
    return jsonify(error=str(e.description)), e.code

# Input validation helper
def validate_student_data(data, is_update=False):
    required_fields = ['student_id', 'name', 'email']
    for field in required_fields:
        if not is_update and field not in data:
            abort(400, description=f"Missing required field: {field}")
        if field in data and not isinstance(data[field], str):
            abort(400, description=f"{field} must be a string")

@app.route('/students', methods=['GET'])
def get_students():
    students = list(students_collection.find({}, {'_id': 0}))
    return jsonify(students)

@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    student = students_collection.find_one({'student_id': student_id}, {'_id': 0})
    if not student:
        abort(404, description="Student not found")
    return jsonify(student)

@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    if not data:
        abort(400, description="No data provided")
    
    validate_student_data(data)
    
    try:
        result = students_collection.insert_one(data)
    except Exception as e:
        abort(400, description=str(e))
    
    return jsonify({'message': 'Student created'}), 201

@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    if not data:
        abort(400, description="No data provided")
    
    validate_student_data(data, is_update=True)
    
    result = students_collection.update_one(
        {'student_id': student_id},
        {'$set': data}
    )
    
    if result.matched_count == 0:
        abort(404, description="Student not found")
    
    return jsonify({'message': 'Student updated'})

@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    result = students_collection.delete_one({'student_id': student_id})
    if result.deleted_count == 0:
        abort(404, description="Student not found")
    return jsonify({'message': 'Student deleted'})

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=6000)