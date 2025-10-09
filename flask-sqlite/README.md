# Flask + SQLite Sample App with Keploy Integration

This is a simple **Student Management REST API** built using Python's Flask framework and SQLite for storage. It demonstrates basic **CRUD operations** (Create, Read, Update, Delete) and showcases how to write **API tests with [Keploy](https://keploy.io)** by auto-capturing HTTP calls as test cases.

---

## 🚀 Features

- 🧑 Add, retrieve, update, and delete students
- 💾 Uses SQLite — no external DB setup required
- 🔌 RESTful API with JSON input/output
- ✅ Auto-generate test cases using [Keploy CLI](https://docs.keploy.io)
- 🔄 Replay & validate API responses with Keploy

---

## 📦 Tech Stack

- **Flask** — Lightweight web framework
- **Flask-SQLAlchemy** — ORM for SQLite
- **SQLite** — Built-in relational DB
- **Keploy** — Testing toolkit for API auto-mocking and regression testing

---

## 🛠 Installation

1. **Clone the repository**
```bash
git clone https://github.com/<your-username>/samples-python.git
cd samples-python/flask-sqlite
```

2. Set up virtual environment (optional)
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install Dependencies
   
```bash
pip install -r requirements.txt
```
4. Run the Flask app

```bash
python app.py
```
---

## API Endpoints

```bash

| Method | Endpoint         | Description          |
| ------ | ---------------- | -------------------- |
| GET    | `/students`      | Get all students     |
| POST   | `/students`      | Add a new student    |
| PUT    | `/students/<id>` | Update student by ID |
| DELETE | `/students/<id>` | Delete student by ID |

```
---

## Sample Curl Commands

### Add a student

```bash
curl -X POST http://localhost:5000/students \
     -H "Content-Type: application/json" \
     -d '{"name": "Alice", "age": 21}'

# Get all students
curl http://localhost:5000/students

# Update student
curl -X PUT http://localhost:5000/students/1 \
     -H "Content-Type: application/json" \
     -d '{"name": "Alice Updated", "age": 22}'

# Delete student
curl -X DELETE http://localhost:5000/students/1

```
---

## Running Keploy Tests

Step 1: Record Tests
Start Keploy in record mode:

```bash
keploy record --command "python app.py"
```
Send some API requests via curl or Postman to generate test cases.

Step 2: Replay Tests
After recording, stop the app and run:

```bash
keploy test --command "python app.py"
```
> Keploy will replay the previously captured requests and validate responses.

## Folder Structure

```bash
flask-sqlite/
├── app.py               # Flask app entry point
├── models.py            # Student model
├── requirements.txt     # Python dependencies
├── keploy.yml           # Keploy config file
├── keploy/              # Auto-generated test cases
└── README.md            # You are here!
```
---

## Contributing
> Want to improve or add another example (e.g. FastAPI, SQLModel, etc.)? Contributions are welcome! Fork this repo, create your example folder, and submit a PR.

## About Keploy
Keploy is a developer-friendly open-source testing toolkit that auto-generates test cases from API calls in real-time and replays them to catch regressions — without writing any test code.

> Built with ❤️ for the Open Source Community.