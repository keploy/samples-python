  curl -X POST -H "Content-Type: application/json" -d '{"student_id": "12345", "name": "John Doe", "age": 20}' http://localhost:6000/students
  curl -X POST -H "Content-Type: application/json" -d '{"student_id": "12346", "name": "Alice Green", "age": 22}' http://localhost:6000/students
  curl -X POST -H "Content-Type: application/json" -d '{"student_id": "12345", "name": "John Doe", "age": 20}' http://localhost:6000/students
  curl -X POST -H "Content-Type: application/json" -d '{"student_id": "12346", "name": "Alice Green", "age": 22}' http://localhost:6000/students
  curl -X POST -H "Content-Type: application/json" -d '{"student_id": "12345", "name": "John Doe", "age": 20}' http://localhost:6000/students
  curl -X POST -H "Content-Type: application/json" -d '{"student_id": "12346", "name": "Alice Green", "age": 22}' http://localhost:6000/students
  
  curl -X POST -H "Content-Type: application/json" -d '{"student_id": "12347", "name": "Bob Brown", "age": 24}' http://localhost:6000/students

  curl http://localhost:6000/students
  curl http://localhost:6000/students/12345
  curl -X PUT -H "Content-Type: application/json" -d '{"name": "Jane Smith", "age": 21}' http://localhost:6000/students/12345
  curl -X DELETE http://localhost:6000/students/12345