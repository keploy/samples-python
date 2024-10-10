# Inventory Management Application

## Overview

A simple Django + MongoDB inventory management application using mongoengine and Django REST Framework to test Keploy integration capabilities using Django and MongoDB.
The endpoints available will be:

1. `GET /api/items/` - List all items
2. `POST /api/items/` - Create a new item
3. `GET /api/items/<id>/` - Retrieve an item by ID
4. `PUT /api/items/<id>/` - Update an item by ID
5. `DELETE /api/items/<id>/` - Delete an item by ID

## Requirements

- Python 3.x
- Django
- mongoengine
- djangorestframework

## Setup Instructions

1. Clone the repository and navigate to project directory.
   ```bash
   git clone https://github.com/keploy/samples-python.git
   cd samples-python/django-mongo/django_mongo
   ```
2. Install Keploy.
   ```bash
    curl --silent -O -L https://keploy.io/install.sh && source install.sh
   ```
3. Start MongoDB instance.
   ```bash
   docker pull mongo
   docker run --name mongodb -d -p 27017:27017 -v mongo_data:/data/db -e MONGO_INITDB_ROOT_USERNAME=<username> -e MONGO_INITDB_ROOT_PASSWORD=<password> mongo
   ```
4. Set up Django appllication.
   ```bash
   python3 -m virtualenv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   ```
5. Capture the testcases.
   ```bash
   keploy record -c "python3 manage.py runserver"
   ```
6. Generate testcases by making API calls.
   ```bash
   # List items
   # GET /api/items/
   curl -X GET http://localhost:8000/api/items/
   ```
   ```bash
   # Create Item
   # POST /api/items/
   curl -X POST http://localhost:8000/api/items/ \
   -H "Content-Type: application/json" \
   -d '{
       "name": "Gadget C",
       "quantity": 200,
       "description": "A versatile gadget with numerous features."
    }'
   ```
   ```bash
   # Retrieve Item
   # GET /api/items/<id>/
   curl -X GET http://localhost:8000/api/items/<id>/
   ```
   ```bash
   # Update Item
   # PUT /api/items/<id>/
   curl -X PUT http://localhost:8000/api/items/6142d21e122bda15f6f87b1d/ \
   -H "Content-Type: application/json" \
   -d '{
       "name": "Updated Widget A",
       "quantity": 120,
       "description": "An updated description for Widget A."
   }'
   ```
   ```bash
   # Delete Item
   # DELETE /api/items/<id>/
   curl -X DELETE http://localhost:8000/api/items/<id>/
   ```
   Replace `<id>` with the actual ID of the item you want to retrieve, update, or delete.

## Run the testcases

Shut down MongoDB, Keploy doesn't need it during tests.
```bash
keploy test -c "python3 manage.py runserver" --delay 10
```