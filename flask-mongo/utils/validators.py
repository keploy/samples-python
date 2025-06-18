import re
from functools import wraps
from flask import jsonify, request
from jsonschema import validate, ValidationError

# Define validation schemas
STUDENT_SCHEMA = {
    "type": "object",
    "properties": {
        "student_id": {
            "type": "string",
            "minLength": 1,
            "pattern": "^[a-zA-Z0-9_-]+$",
            "error_message": "Student ID must be a non-empty alphanumeric string"
        },
        "name": {
            "type": "string",
            "minLength": 2,
            "maxLength": 100,
            "pattern": "^[a-zA-Z\\s'-]+$",
            "error_message": "Name must be a valid string between 2-100 characters"
        },
        "age": {
            "type": "integer",
            "minimum": 1,
            "maximum": 120,
            "error_message": "Age must be a positive integer between 1 and 120"
        },
        "email": {
            "type": "string",
            "format": "email",
            "error_message": "Invalid email format"
        }
    },
    "required": ["student_id", "name", "age"],
    "additionalProperties": False
}

def validate_student_data(data):
    """Validate student data against the schema"""
    try:
        validate(instance=data, schema=STUDENT_SCHEMA)
        return None  # No errors
    except ValidationError as e:
        # Extract the error message from the schema
        path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else ""
        field = path.split(".")[-1] if path else "request body"
        
        # Get custom error message from schema if available
        if "properties" in STUDENT_SCHEMA and field in STUDENT_SCHEMA["properties"]:
            if "error_message" in STUDENT_SCHEMA["properties"][field]:
                return f"Validation error in {field}: {STUDENT_SCHEMA['properties'][field]['error_message']}"
        
        return f"Validation error in {field}: {e.message}"

def validate_json_content_type(f):
    """Decorator to validate content type is application/json"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json:
                return jsonify({
                    'error': 'Content-Type must be application/json'
                }), 415
        return f(*args, **kwargs)
    return decorated_function

def validate_student_required(f):
    """Decorator to validate student data in request"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No input data provided'
            }), 400
            
        error = validate_student_data(data)
        if error:
            return jsonify({
                'error': error
            }), 400
            
        return f(*args, **kwargs)
    return decorated_function
