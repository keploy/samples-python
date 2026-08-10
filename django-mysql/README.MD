## Django MySQL CRUD Application

This application is a simple Employee Management System built with Django and MySQL. It allows you to create, retrieve, update, and delete employee records via RESTful API endpoints. The application is containerized using Docker, making it easy to deploy and run in different environments. The backend is powered by Django, and the MySQL database is used to store employee information.

## Prerequisites

* Docker

## Steps to Run the Application

### 1. Build and Run MySQL Database Container

Run the db:

```bash
docker run --name mySQL --network keploy-network -e MYSQL_ROOT_PASSWORD=keploy -e MYSQL_DATABASE=keploy_db -e MYSQL_USER=admin -e MYSQL_PASSWORD=keploy -p 3306:3306 -d mysql
```

### 2. Build and Run Django Application Container

In the project root directory, run:

```bash
docker build --build-arg HOST_PWD="$(pwd)" -t py-app .

docker run --name django-app --net keploy-network -p 8000:8000 -v "$(pwd):$(pwd)" --rm py-app
```

### 3. API Endpoints

• **Create Employee (POST):** [http://localhost:8000/api/employee/create/](http://localhost:8000/api/employee/create/)

• **Get Employee by ID (GET):** [http://localhost:8000/api/employee/{id}/](http://localhost:8000/api/employee/{id}/)

• **Get All Employees (GET):** [http://localhost:8000/api/employee/](http://localhost:8000/api/employee/)

• **Update Employee (PUT):** [http://localhost:8000/api/employee/update/{id}/](http://localhost:8000/api/employee/update/{id}/)

• **Delete Employee (DELETE):** [http://localhost:8000/api/employee/delete/{id}/](http://localhost:8000/api/employee/delete/{id}/)

### Example Request Payload for Creating an Employee:

```bash
curl -X POST http://localhost:8000/api/employee/create/ -H "Content-Type: application/json" -d '{"name": "John Doe", "years_of_experience": 5, "field": "Computer Science", "company": "TechCorp"}'
```

### Notes:

> Django application runs on port 8000.

## Testing the APIs

Use the following curl commands to test the APIs after running the application:

### POST Request to create an employee

```bash
curl -X POST http://localhost:8000/api/employee/create/ -H "Content-Type: application/json" -d '{"name": "John Doe", "years_of_experience": 5, "field": "Computer Science", "company": "TechCorp"}'
```

### GET Request to fetch all employees

```bash
curl -X GET http://localhost:8000/api/employee/
```

### GET Request to fetch an employee by ID

```bash
curl -X GET http://localhost:8000/api/employee/1/
```

### PUT Request to update an employee

```bash
curl -X PUT http://localhost:8000/api/employee/update/1/ -H "Content-Type: application/json" -d '{"name": "Jane Doe", "years_of_experience": 6, "field": "Data Science", "company": "TechCorp"}'
```

### DELETE Request to delete an employee

```bash
curl -X DELETE http://localhost:8000/api/employee/delete/1/
```