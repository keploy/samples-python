import os
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson import ObjectId
from config import get_config
from utils.logger import setup_logging, get_logger
from utils.validators import validate_json_content_type, validate_student_required
from utils.errors import (
    APIError, NotFoundError, ValidationError, 
    ConflictError, register_error_handlers
)

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(get_config())

# Initialize CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[app.config.get('RATELIMIT_DEFAULT', '200 per day')]
)

# Setup logging
setup_logging(app.config)
logger = get_logger(__name__)


# Initialize MongoDB
client = MongoClient(app.config['MONGO_URI'])
db = client[app.config['MONGO_DB_NAME']]
students_collection = db['students']

# Create indexes
students_collection.create_index('student_id', unique=True)

# Initialize Flask-RESTx
api = Api(
    app,
    version='1.0',
    title='Student Management API',
    description='A RESTful API for managing student records',
    doc='/api/docs',
    default='Students',
    default_label='Student operations',
    validate=True
)

# Define models
student_model = api.model('Student', {
    'student_id': fields.String(required=True, description='Unique student identifier'),
    'name': fields.String(required=True, description='Student full name'),
    'age': fields.Integer(required=True, description='Student age'),
    'email': fields.String(description='Student email address')
})

# Namespace
ns = Namespace('students', description='Student operations')

@ns.route('/')
class StudentList(Resource):
    @ns.doc('list_students')
    @ns.marshal_list_with(student_model)
    @limiter.limit("100 per hour")
    def get(self):
        """List all students"""
        logger.info('Fetching all students')
        try:
            students = list(students_collection.find({}, {'_id': 0}))
            return students
        except Exception as e:
            logger.error(f'Error fetching students: {str(e)}')
            raise APIError('Failed to retrieve students', status_code=500)
    
    @ns.doc('create_student')
    @ns.expect(student_model)
    @ns.marshal_with(student_model, code=201)
    @validate_json_content_type
    @validate_student_required
    @limiter.limit("50 per hour")
    def post(self):
        """Create a new student"""
        data = request.get_json()
        logger.info(f'Creating new student: {data}')
        
        try:
            # Check if student already exists
            if students_collection.find_one({"student_id": data['student_id']}):
                raise ConflictError(f"Student with ID {data['student_id']} already exists")
            
            # Insert new student
            result = students_collection.insert_one(data)
            if not result.inserted_id:
                raise APIError('Failed to create student', status_code=500)
                
            logger.info(f'Student created with ID: {data["student_id"]}')
            return data, 201
            
        except DuplicateKeyError:
            raise ConflictError(f"Student with ID {data['student_id']} already exists")
        except Exception as e:
            logger.error(f'Error creating student: {str(e)}')
            raise APIError('Failed to create student', status_code=500)

@ns.route('/<string:student_id>')
@ns.param('student_id', 'The student identifier')
@ns.response(404, 'Student not found')
class Student(Resource):
    @ns.doc('get_student')
    @ns.marshal_with(student_model)
    def get(self, student_id):
        """Fetch a student given its identifier"""
        logger.info(f'Fetching student with ID: {student_id}')
        student = students_collection.find_one(
            {'student_id': student_id}, 
            {'_id': 0}
        )
        
        if not student:
            logger.warning(f'Student not found with ID: {student_id}')
            raise NotFoundError('Student not found')
            
        return student
    
    @ns.doc('update_student')
    @ns.expect(student_model)
    @ns.marshal_with(student_model)
    @validate_json_content_type
    @validate_student_required
    def put(self, student_id):
        """Update a student"""
        data = request.get_json()
        logger.info(f'Updating student with ID: {student_id}, data: {data}')
        
        try:
            # Don't allow changing student_id
            if 'student_id' in data and data['student_id'] != student_id:
                raise ValidationError('Cannot change student_id')
            
            # Update the student
            result = students_collection.find_one_and_update(
                {'student_id': student_id},
                {'$set': data},
                return_document=ReturnDocument.AFTER,
                projection={'_id': 0}
            )
            
            if not result:
                raise NotFoundError('Student not found')
                
            logger.info(f'Student updated: {student_id}')
            return result
            
        except Exception as e:
            logger.error(f'Error updating student {student_id}: {str(e)}')
            if isinstance(e, APIError):
                raise
            raise APIError('Failed to update student', status_code=500)
    
    @ns.doc('delete_student')
    @ns.response(204, 'Student deleted')
    def delete(self, student_id):
        """Delete a student"""
        logger.info(f'Deleting student with ID: {student_id}')
        
        try:
            result = students_collection.delete_one({'student_id': student_id})
            if result.deleted_count == 0:
                raise NotFoundError('Student not found')
                
            logger.info(f'Student deleted: {student_id}')
            return '', 204
            
        except Exception as e:
            logger.error(f'Error deleting student {student_id}: {str(e)}')
            if isinstance(e, APIError):
                raise
            raise APIError('Failed to delete student', status_code=500)

# Register the namespace
api.add_namespace(ns, path='/api/students')

# Register error handlers
register_error_handlers(app)

# Health check endpoint
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        client.admin.command('ping')
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        logger.error(f'Health check failed: {str(e)}')
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    try:
        # Log startup
        logger.info('Starting Student Management API...')
        logger.info(f'Environment: {app.config["ENV"]}')
        logger.info(f'Debug mode: {app.config["DEBUG"]}')
        
        # Run the app
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 6000)),
            debug=app.config.get('DEBUG', False)
        )
    except Exception as e:
        logger.critical(f'Failed to start application: {str(e)}')
        raise
