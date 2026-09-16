from flask import Blueprint, request, jsonify, current_app

students_bp = Blueprint("students", __name__)

@students_bp.route("/", methods=["GET"])
def get_students():
    students = list(current_app.db.students.find({}, {"_id": 0}))
    return jsonify(students), 200

@students_bp.route("/<student_id>", methods=["GET"])
def get_student(student_id):
    student = current_app.db.students.find_one({"student_id": student_id}, {"_id": 0})
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student), 200

@students_bp.route("/", methods=["POST"])
def create_student():
    new_student = request.json
    current_app.db.students.insert_one(new_student)
    return jsonify({"message": "Student created successfully"}), 201

@students_bp.route("/<student_id>", methods=["PUT"])
def update_student(student_id):
    updated_student = request.json
    result = current_app.db.students.update_one({"student_id": student_id}, {"$set": updated_student})
    if result.matched_count == 0:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student updated successfully"}), 200

@students_bp.route("/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    result = current_app.db.students.delete_one({"student_id": student_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({"message": "Student deleted successfully"}), 200
