from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from bson import ObjectId

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

client = MongoClient('mongodb://localhost:27017/')
db = client['task_manager']
collection = db['tasks']

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    task = {
        'title': data['title'],
        'description': data['description']
    }
    result = collection.insert_one(task)
    return jsonify({'message': 'Task created successfully', 'id': str(result.inserted_id)}), 201

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    tasks = []
    for task in collection.find():
        tasks.append({
            'id': str(task['_id']),
            'title': task['title'],
            'description': task['description']
        })
    return jsonify({'tasks': tasks})

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    updated_task = {
        'title': data['title'],
        'description': data['description']
    }
    try:
        result = collection.update_one({'_id': ObjectId(task_id)}, {'$set': updated_task})
        if result.modified_count == 0:
            return jsonify({'error': 'Task not found or no changes were made'}), 404
        else:
            return jsonify({'message': 'Task updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    collection.delete_one({'_id': ObjectId(task_id)})
    return jsonify({'message': 'Task deleted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
