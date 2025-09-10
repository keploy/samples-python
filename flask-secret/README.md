# Flask Secret Generator API

This application is a Flask-based API that generates synthetic secrets and API keys for testing purposes. It provides deterministic secret generation across multiple endpoints, making it perfect for testing secret scanning tools like GitLeaks and other security scanners.

## Table of Contents

- [Introduction](#introduction)
- [Pre-Requisites](#pre-requisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Testing with Keploy](#testing-with-keploy)
- [Wrapping Up](#wrapping-up)

# Introduction

🔐 Dive into the world of synthetic secret generation and see how seamlessly Keploy integrates with [Flask](https://flask.palletsprojects.com/) for API testing. This application generates realistic-looking secrets for various cloud providers and services in a deterministic way, making it perfect for security testing workflows! 🎢

## Pre-Requisites 🛠️

- Python 3.7+ installed on your system
- pip (Python package installer)
- Install WSL (`wsl --install`) for <img src="https://keploy.io/docs/img/os/windows.png" alt="Windows" width="3%" /> Windows.

## Optional 🛠️

- Install Colima( `brew install colima && colima start` ) for <img src="https://keploy.io/docs/img/os/macos.png" alt="MacOS" width="3%" /> MacOS.

## Installation 📥

### Install Dependencies

First, navigate to the project directory and setup python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Install Keploy

```bash
 curl --silent -O -L https://keploy.io/install.sh && source install.sh
```

## Running the Application 🚀

Start the Flask application:

```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints 📡

The application provides the following endpoints:

### Health Check
```bash
curl -s http://localhost:8000/health
```

### Secret Generation Endpoints

**Get secrets from /secret1:**
```bash
curl -s http://localhost:8000/secret1
```

**Get secrets from /secret2:**
```bash
curl -s http://localhost:8000/secret2
```

**Get secrets from /secret3:**
```bash
curl -s http://localhost:8000/secret3
```

Each endpoint returns a deeply nested JSON payload containing various types of synthetic secrets including:
- AWS Access Keys and Secret Keys
- GitHub Personal Access Tokens
- Slack Webhook URLs
- Stripe Live Keys
- Google API Keys
- MongoDB URIs
- PostgreSQL URLs
- And many more...

## Testing with Keploy 🧪

### Lights, Camera, Record! 🎥

Capture test cases by recording API interactions:

```shell
keploy record -c "python main.py"
```

### Generate Test Cases

Make some API calls to generate test cases. You can use curl, Postman, or any HTTP client:

**Make GET requests to all secret endpoints:**

```bash
curl -s http://localhost:8000/secret1
curl -s http://localhost:8000/secret2  
curl -s http://localhost:8000/secret3
```

You will now see a folder named `keploy` with your recorded tests.

### Run Tests

Execute the recorded tests:

```shell
keploy test -c "python main.py"
```

## Features ✨

- **Deterministic Generation**: All secrets are generated deterministically using fixed seeds
- **Realistic Format**: Secrets follow the actual format patterns of real services
- **Multiple Providers**: Supports AWS, GitHub, Slack, Stripe, Google, MongoDB, PostgreSQL, and more
- **Nested Payloads**: Returns complex, deeply nested JSON structures
- **Testing Ready**: Perfect for security scanner testing and API testing workflows

## Wrapping it up 🎉

Congrats on exploring the Flask Secret Generator API! You've seen how Keploy can seamlessly integrate with Flask applications for comprehensive API testing. This tool is perfect for testing secret scanning tools and security workflows without exposing real credentials.

Happy coding! ✨👩‍💻👨‍💻✨

<br/>
