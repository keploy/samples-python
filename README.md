<h1 align="center"> Keploy Python Sample Applications </h1>
<p align="center">

  <a href="CODE_OF_CONDUCT.md" alt="Contributions welcome">
    <img src="https://img.shields.io/badge/Contributions-Welcome-brightgreen?logo=github" /></a>

  <a href="https://join.slack.com/t/keploy/shared_invite/zt-357qqm9b5-PbZRVu3Yt2rJIa6ofrwWNg" alt="Slack">
    <img src=".github/slack.svg" /></a>

  <a href="https://opensource.org/licenses/Apache-2.0" alt="License">
    <img src=".github/License-Apache_2.0-blue.svg" /></a>
</p>

This repo contains the samples for [Keploy's](https://keploy.io) integration with Python-based Application. Please feel free to contribute if you'd like submit a sample for another use-case or library.

> **Note** :- Issue Creation is disabled on this Repository, please visit [here](https://github.com/keploy/keploy/issues/new/choose) to submit Issue.

## Python Sample Apps with Keploy

1. [Flask-Mongo](https://github.com/keploy/samples-python/tree/main/flask-mongo) - This application is a simple task management API built using Python's Flask framework and MongoDB for data storage. It allows you to perform basic CRUD (Create, Read, Update, Delete) operations on student records. The API supports CORS (Cross-Origin Resource Sharing) to facilitate cross-domain requests.

2. [Django-Postgres](https://github.com/keploy/samples-python/tree/main/django-postgres) - This is an application to perform basic CRUD (Create, Read, Update, Delete) operations on user records built using Python's Django framework and PostgreSQL for data storage.

3. [FastAPI-Postgres](https://github.com/keploy/samples-python/tree/main/fastapi-postgres) - This application is a student management API built using Python's FastAPI and PostgreSQL for data storage. It allows you to perform basic CRUD (Create, Read, Update, Delete) operations on student data.

4. [FastAPI-Twilio](https://github.com/keploy/samples-python/tree/main/fastapi-twilio) - This application is a SMS sending API built using Python's FastAPI and Twilio for their SMS sharing service.

5. [Flask-Redis](https://github.com/keploy/samples-python/tree/main/flask-redis) - This Flask-based application provides a book management system utilizing Redis for caching and storage. It supports adding, retrieving, updating, and deleting book records, with optimized search functionality and cache management for improved performance. The API endpoints ensure efficient data handling and quick access to book information.

## 🛡️ Ensuring Proper Code Coverage with Keploy

When running Python samples with Keploy, it's important to make sure coverage data is saved correctly when the app shuts down. To avoid issues (like missing `coverage.keploy` files), use one of these methods:

### ✅ Option 1: Graceful Shutdown in Your App

Update your app’s main file with:

```python
import signal
import sys

def handle_exit(sig, frame):
    print("Gracefully shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

## Community Support ❤️

### 🤔 Questions?

Reach out to us. We're here to help!

[![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)](https://join.slack.com/t/keploy/shared_invite/zt-357qqm9b5-PbZRVu3Yt2rJIa6ofrwWNg)
[![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/company/keploy/)
[![YouTube](https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white)](https://www.youtube.com/channel/UC6OTg7F4o0WkmNtSoob34lg)
[![Twitter](https://img.shields.io/badge/Twitter-%231DA1F2.svg?style=for-the-badge&logo=Twitter&logoColor=white)](https://twitter.com/Keployio)

### 💖 Let's Build Together!
