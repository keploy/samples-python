<h1 align="center"> Keploy Python Sample Applications </h1>
<p align="center">

  <a href="CODE_OF_CONDUCT.md" alt="Contributions welcome">
    <img src="https://img.shields.io/badge/Contributions-Welcome-brightgreen?logo=github" /></a>

  <a href="https://join.slack.com/t/keploy/shared_invite/zt-357qqm9b5-PbZRVu3Yt2rJIa6ofrwWNg" alt="Slack">
    <img src=".github/slack.svg" /></a>

  <a href="https://opensource.org/licenses/Apache-2.0" alt="License">
    <img src=".github/License-Apache_2.0-blue.svg" /></a>
</p>

## Introduction

This repository contains sample applications demonstrating [Keploy's](https://keploy.io) integration with various Python-based web frameworks and databases. Keploy is an API testing platform that automatically generates test cases and data mocks from API calls, making testing more efficient and comprehensive.

These samples showcase how to integrate Keploy with different Python web frameworks and databases, providing practical examples for your own projects. Each sample includes detailed setup instructions and demonstrates key Keploy features like test generation, data mocking, and test execution.

> **Note** :- Issue Creation is disabled on this Repository, please visit [here](https://github.com/keploy/keploy/issues/new/choose) to submit Issue.

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Sample Applications](#python-sample-apps-with-keploy)
- [Getting Started](#getting-started)
- [Running the Samples](#running-the-samples)
- [Contributing](#contributing)
- [Community Support](#community-support-️)

## Prerequisites

Before running any sample application, make sure you have the following installed:

- Python 3.7+ 
- [Keploy CLI](https://keploy.io/docs)
- Docker and Docker Compose (for applications using containers)
- Database systems as required by individual samples (MongoDB, PostgreSQL, Redis, etc.)

## Python Sample Apps with Keploy

1. [Flask-Mongo](https://github.com/keploy/samples-python/tree/main/flask-mongo) - A simple task management API built using Flask and MongoDB for data storage. It demonstrates CRUD operations on student records with CORS support.

2. [Django-Postgres](https://github.com/keploy/samples-python/tree/main/django-postgres) - A user management application using Django and PostgreSQL for performing CRUD operations on user records.

3. [FastAPI-Postgres](https://github.com/keploy/samples-python/tree/main/fastapi-postgres) - A student management API built with FastAPI and PostgreSQL for CRUD operations on student data.

4. [FastAPI-Twilio](https://github.com/keploy/samples-python/tree/main/fastapi-twilio) - A SMS sending API built using FastAPI and Twilio services.

5. [Flask-Redis](https://github.com/keploy/samples-python/tree/main/flask-redis) - A book management system using Flask with Redis for caching and storage, demonstrating optimized search functionality.

6. [Django-Mongo](https://github.com/keploy/samples-python/tree/main/django-mongo) - An inventory management application using Django, MongoDB, mongoengine, and Django REST Framework.

7. [Flask-PostgreSQL](https://github.com/keploy/samples-python/tree/main/flask_postgresql_app) - A Flask application integrated with PostgreSQL database.

8. [Sanic-Mongo](https://github.com/keploy/samples-python/tree/main/sanic-mongo) - A movie management API built using Sanic framework and MongoDB for data storage.

9. [Sanic-Postgres](https://github.com/keploy/samples-python/tree/main/sanic-postgres) - An employee management API built with Sanic framework and PostgreSQL.

## Getting Started

To get started with any sample application:

1. Install Keploy CLI:
   ```bash
   curl --silent -O -L https://keploy.io/install.sh && source install.sh
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/keploy/samples-python.git
   cd samples-python
   ```

3. Navigate to the sample application directory of your choice:
   ```bash
   cd <sample-app-directory>
   ```

4. Follow the specific README.md instructions in that directory.

## Running the Samples

Each sample application follows a similar pattern:

1. **Installation**: Install dependencies and set up the required database
2. **Record Mode**: Capture API calls using Keploy
3. **Test Mode**: Run tests using the generated test cases

For detailed instructions, refer to the README.md file in each sample application directory.

## Framework and Database Coverage

The samples in this repository cover a wide range of Python frameworks and databases:

### Frameworks
- Flask
- Django
- FastAPI
- Sanic

### Databases
- MongoDB
- PostgreSQL
- Redis

## Contributing

Contributions are welcome! If you'd like to submit a sample for another use-case, framework, or database integration, please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-sample`)
3. Commit your changes (`git commit -m 'Add new sample for XYZ framework'`)
4. Push to the branch (`git push origin feature/new-sample`)
5. Open a Pull Request

Please ensure your sample application includes:
- Clear setup and usage instructions
- Properly documented code
- Demonstration of Keploy's key features
- Tests showing Keploy integration

## Community Support ❤️

### 🤔 Questions?

Reach out to us. We're here to help!

[![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)](https://join.slack.com/t/keploy/shared_invite/zt-357qqm9b5-PbZRVu3Yt2rJIa6ofrwWNg)
[![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/company/keploy/)
[![YouTube](https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white)](https://www.youtube.com/channel/UC6OTg7F4o0WkmNtSoob34lg)
[![Twitter](https://img.shields.io/badge/Twitter-%231DA1F2.svg?style=for-the-badge&logo=Twitter&logoColor=white)](https://twitter.com/Keployio)

### 💖 Let's Build Together!