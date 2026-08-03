from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from config import Config
from routes.students import students_bp
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # MongoDB connection
    client = MongoClient(Config.MONGO_URI)
    db = client['studentsdb']
    app.db = db

    # Register blueprint
    app.register_blueprint(students_bp, url_prefix="/api/students")

    @app.route("/")
    def home():
        return {"message": "Student API is running"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=6000, debug=True)
