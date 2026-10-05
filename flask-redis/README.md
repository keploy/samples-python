# flask-redis

A sample App using flask and redis

## Setup application

1. Clone the repository and move to flask-redis folder
2. Create a .env file and copy-paste below credentials:

```bash
REDIS_HOST=redis
REDIS_PORT=6379
```

# Installing Redis

```sh
brew install redis
```
If homebrew is not installed, then go to https://brew.sh/ and install it.

```bash
git clone https://github.com/keploy/samples-typescript && cd samples-typescript/flask-redis

# Install the dependencies
pip3 install -r requirements.txt
```

# Installing Keploy

Let's get started by setting up the Keploy alias with this command:

```sh
curl -O https://raw.githubusercontent.com/keploy/keploy/main/keploy.sh && source keploy.sh
```

## Using Keploy :

There are 2 ways you can run this sample application.

1. [Natively on Linux/WSL](#natively-on-ubuntuwsl)
2. [Using Docker](#running-sample-app-using-docker)

# Natively on Ubuntu/WSL

> **Note:** You no longer need to download a `ca.crt` or run `setup_ca.sh`.
> Keploy generates its MITM CA per run and sets the trust environment variables
> for the app it launches automatically. (The old `pkg/core/proxy/asset/` URLs
> are retired.)

1. **Start the redis server:**
   ```sh
   redis-server
   ```
   This command starts the redis server.

## Capture the test cases

1. **Start recording tests:**
   ```bash
   sudo -E env "PATH=$PATH" keploybin record -c 'python3 app.py'
   ```

## Let's Generate the test cases

Make API Calls using Hoppscotch, Postman or cURL command. Keploy will capture those calls to generate test suites containing test cases and data mocks.

1. Refer to flask-redis/api.txt to make api calls.

2. **Observe terminal output:**
   Let's go ahead and create a few more test cases for different endpoints!

## Running the test cases

1. **Start the application:**

   ```bash
   python3 app.py
   ```

2. **Run the recorded tests:**

   ```bash
   sudo -E env "PATH=$PATH" keploybin test -c 'python3 app.py' --delay 10
   ```

3. **Observe test run results:**
   _Voila!! Our test cases have passed 🌟_

---

# Using Docker

Since we have to setup our app using docker(make sure your docker is running)

## Create a custom network for Keploy since we are using the Docker

```bash
docker network create keploy-network
```

## Capture the testcases

We will run the keploy in record mode with docker-compose to start our application:-

```bash
keploy record -c "sudo docker-compose up" --containerName "flask-web"

```

#### Let's generate the testcases.

Make API Calls using [Hoppscotch](https://hoppscotch.io), [Postman](https://postman.com) or curl command. Keploy with capture those calls to generate the test-suites containing testcases and data mocks.

1. Refer to flask-redis/api.txt to make api calls

## Running the testcases

```bash
keploy test -c 'sudo docker-compose up' --containerName "flask-web" --delay 10
```

_Voila!! Our testcases has passed 🌟_
