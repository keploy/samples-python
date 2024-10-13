# User Management API


## Overview

This is a Flask-based web application that uses PostgreSQL as its database.
This API allows you to manage users by performing CRUD operations. It is containerized using Docker for easy deployment, and uses PostgreSQL as the database.
Keploy is integrated for automated test case generation and testing.

The endpoints available will be:

1. `GET /` - Home Route
2. `GET /users` - List all users
3. `POST /users` - Create a new user
4. `PUT /users/<id>` - Update a user
5. `DELETE /users/<id>` - Delete a user



## Setup Instructions

1. Clone the repository and navigate to project directory.
   ```bash
   git clone https://github.com/keploy/samples-python.git
   cd samples-python/flask_postgresql_app
   ```
2. Install Keploy.
   ```bash
    curl --silent -O -L https://keploy.io/install.sh && source install.sh
   ```
3. Build and run the Docker containers:
   ```bash
   docker compose up --build
   ```
4. Access the application:
   Once the containers are running, the Flask app will be available at:
   ```bash
   http://localhost:5000
   ```
5. Capture the testcases.
   ```bash
   keploy record -c "docker compose up" --container-name "flask_web_app" 
   ```
6. Generate testcases by making API calls.
   ## Home Route
   ### GET /
   ```bash
   curl -X GET http://localhost:5000
   ```
   ## Retrieves a list of all users.
   ### GET /users
   ```bash
   curl -X GET http://localhost:5000/users 
   ```
   ## Create a new user by providing a name.
   ### POST /users
   ```bash
   curl -X POST http://localhost:5000/users -H "Content-Type: application/json" -d '{"name": "Harsh"}'
   ``` 
   ### Retrieve a user by their ID.
   ## GET /users/id
   ```bash
   curl -X GET http://localhost:5000/users/<id>
   ```
   ## Update the name of a user by their ID.
   ### PUT /users/id
   ```bash
    curl -X PUT http://localhost:5000/users/<id> -H "Content-Type: application/json" -d '{"name": "Updated Name"}'
   ```
   ## Delete a user by their ID
   ### DELETE /users/id
   ```bash
   curl -X DELETE http://localhost:5000/users/<id>
   ```
   Replace `<id>` with the actual ID of the item you want to retrieve, update, or delete.

## Run the testcases
```bash
keploy test -c "docker compose up" --container-name "flask_web_app"
```

