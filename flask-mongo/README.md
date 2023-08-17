This application is a simple student management API built using Python's Flask framework and MongoDB for data storage. It allows you to perform basic CRUD (Create, Read, Update, Delete) operations on student records. The API supports CORS (Cross-Origin Resource Sharing) to facilitate cross-domain requests.


Usage:

1. Get List of Students: Retrieve a list of all students.
```
curl http://localhost:6000/students
```

2. Get Student by ID: Retrieve details of a specific student using their student ID.
```
curl http://localhost:6000/students/12345
```

3. Create a New Student: Add a new student record to the database.

```
curl -X POST -H "Content-Type: application/json" -d '{"student_id": "12345", "name": "John Doe", "age": 20}' http://localhost:6000/students
```

4. Update Student Information: Update details of an existing student using their student ID.
```
curl -X PUT -H "Content-Type: application/json" -d '{"name": "Jane Smith", "age": 21}' http://localhost:6000/students/12345
```

5. Delete Student: Delete a student record by their student ID.
```
curl -X DELETE http://localhost:6000/students/12345
```