from flask import Flask, request, jsonify
from marshmallow import ValidationError
from nanoid import generate
import redis
import json
from schema import CreateTodoSchema, UpdateTodoSchema

app = Flask(__name__)

db = redis.Redis(
  host='localhost',
  port=6379,
  decode_responses=True
)

@app.route('/')
def get_status():
    return jsonify({ "status": "ok" })


@app.route("/todos", methods=["GET"])
def get_todos():
    keys = db.keys()
    json_data = []
    for key in keys:
        data = db.get(key)
        json_data.append({"id": key, **json.loads(data)})
    return jsonify(json_data), 200



@app.route("/todos/<id>", methods=["GET"])
def get_todo(id: str):
    data = db.get(id)
    if data is None:
        return jsonify({"message": "Data not found."}), 404
    
    json_data = {"id": id, **json.loads(data)}
    return jsonify(json_data), 200


@app.route("/todos/", methods=["POST"])
def create_todos():
    id = generate(size=6)
    schema = CreateTodoSchema()
    try:
        body = schema.load(request.json)
    except ValidationError as error:
        return jsonify({"errors": error.messages}), 422
    db.set(id, json.dumps(body))
    return jsonify({"success": True, "data": {"id": id, **body}}), 200


@app.route("/todos/<id>", methods=["PUT"])
def update_todos(id: str):
    data = db.get(id)
    if data is None:
        return jsonify({ "message": "No todo found." }), 404
    
    json_data = json.loads(data)
    schema = UpdateTodoSchema()
    try:
        body = schema.load(request.json)
    except ValidationError as error:
        return jsonify({"errors": error.messages}), 422    

    for key, value in body.items():
        if value is not None:
            json_data[key] = value

    db.set(id, json.dumps(json_data))
    json_data = {"id": id, **json_data}
    return jsonify(json_data), 200


@app.route("/todos/<id>", methods=["DELETE"])
def delete_todo(id: str):
    status = db.delete(id)
    if not status:
        return jsonify({ "message" : "Deletion failed.", status: 0 }), 400
    return jsonify({"success": True}), 200