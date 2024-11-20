# Employee Management API

This application is a simple employee management API built using Python's Sanic framework and PostgreSQL for data storage. It allows you to perform basic CRUD (Create, Read, Update, Delete) operations on employee records.

## Table of Contents

- [Introduction](#introduction)
- [Pre-Requisites](#pre-requisites)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
  - [Create Employee](#create-employee)
  - [Get All Employees](#get-all-employees)
  - [Get Employee by ID](#get-employee-by-id)
  - [Update Employee](#update-employee)
  - [Delete Employee](#delete-employee)
- [Testing](#testing)
- [Wrapping it up](#wrapping-it-up)

## Introduction

🪄 Dive into the world of Employee Management and see how seamlessly Keploy integrated with Sanic and PostgreSQL. Buckle up, it's gonna be a fun ride! 🎢

## Pre-Requisites 🛠️

Before you begin, ensure you have the following installed:

- **Python 3.x**: The programming language used for this application. You can download it from [python.org](https://www.python.org/downloads/).
- **PostgreSQL**: The database system used for storing employee data. You can download it from [postgresql.org](https://www.postgresql.org/download/).

## Installation 📥

Once you have the prerequisites set up, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/keploy/sample-python.git
   cd sample-python
Install the required Python packages:

```bash
pip install -r requirements.txt
```

Set up your PostgreSQL database and update the connection settings in your application as needed.

Install the latest Keploy binary:

```bash
curl --silent --location "https://github.com/keploy/keploy/releases/latest/download/keploy_linux_amd64.tar.gz" | tar xz -C /tmp
sudo mkdir -p /usr/local/bin && sudo mv /tmp/keploy /usr/local/bin && keploy
```
Add alias for Keploy:

```bash
alias keploy='sudo docker run --pull always --name keploy-v2 -p 16789:16789 --privileged --pid=host -it -v "$(pwd)":/files -v /sys/fs/cgroup:/sys/fs/cgroup -v /sys/kernel/debug:/sys/kernel/debug -v /sys/fs/bpf:/sys/fs/bpf -v /var/run/docker.sock:/var/run/docker.sock -v '"$HOME"'/.keploy-config:/root/.keploy-config -v '"$HOME"'/.keploy:/root/.keploy --rm ghcr.io/keploy/keploy'
```
Install the dependencies:

```bash
pip3 install -r requirements.txt
```
API Endpoints
Create Employee
To add a new employee:

```bash
curl -X POST http://localhost:8000/employees \
-H "Content-Type: application/json" \
-d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "position": "Developer",
    "salary": 60000
}'
```
Get All Employees
To retrieve all employees:

```bash
curl -X GET http://localhost:8000/employees
```

Get Employee by ID
To retrieve a specific employee by ID:

```bash
curl -X GET http://localhost:8000/employees/1
```
Update Employee
To update an existing employee's details:

```bash
curl -X PUT http://localhost:8000/employees/1 \
-H "Content-Type: application/json" \
-d '{
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@example.com",
    "position": "Senior Developer",
    "salary": 80000
}'
```
Delete Employee
To delete an employee:

```bash
curl -X DELETE http://localhost:8000/employees/1
```
Testing
Capture Test Cases
Capture the test cases using Keploy:

```bash
keploy record -c "python3 server.py"
```
Run Tests
Run the tests:

```bash
keploy test -c "python3 server.py"
```
Wrapping it up 🎉
Congrats on the journey so far! You've seen how to manage employees seamlessly with Keploy, Sanic, and PostgreSQL. Keep exploring, innovating, and creating! With the right tools, anything's possible. 😊🚀

Happy coding! ✨👩‍💻👨‍💻✨