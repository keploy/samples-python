from flask import Flask
from routes.book_routes import book

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(book, url_prefix="/books")

@app.route('/', methods=['GET'])
def hello():
    return {"message": "Welcome to the Book Management System!"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
