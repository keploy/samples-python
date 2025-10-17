from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

client = MongoClient('mongodb://mongo:27017/')
db = client['studentsdb']
students_collection = db['students']

@app.route('/students', methods=['GET'])
def get_students():
    students = list(students_collection.find({}, {'_id': 0}))
    return jsonify(students)

@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    student = students_collection.find_one({'student_id': student_id}, {'_id': 0})
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(student)

@app.route('/students', methods=['POST'])
def create_student():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    new_student = request.get_json()
    students_collection.insert_one(new_student)
    return jsonify({'message': 'Student created successfully'}), 201

@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    updated_student = request.get_json()
    result = students_collection.update_one({'student_id': student_id}, {'$set': updated_student})
    if result.matched_count == 0:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify({'message': 'Student updated successfully'})

@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    result = students_collection.delete_one({'student_id': student_id})
    if result.deleted_count == 0:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify({'message': 'Student deleted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)