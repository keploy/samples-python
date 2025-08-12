# Flask-MySQL Sample Application

This application is a comprehensive financial management API built using Python's Flask framework and MySQL for data storage. It provides various endpoints for handling clients, accounts, transactions, and generating financial reports, all secured with JWT authentication.

# Introduction

🪄 Dive into the world of Financial APIs and see how seamlessly Keploy integrated with [Flask](https://flask.palletsprojects.com/en/3.0.x/) and [MySQL](https://www.mysql.com/). Buckle up, it's gonna be a fun ride! 🎢

## Pre-Requisite 🛠️

- Install WSL (`wsl --install`) for <img src="https://keploy.io/docs/img/os/windows.png" alt="Windows" width="3%" /> Windows.

#### Optional 🛠️

- Install Colima( `brew install colima && colima start` ) for <img src="https://keploy.io/docs/img/os/macos.png" alt="MacOS" width="3%" /> MacOs.

## Install Keploy

- Install Keploy CLI using the following command:

```bash
curl -O -L https://keploy.io/install.sh && source install.sh
```

## Get Started! 🎬

## Setup the MySQL Database 📦

First, create the docker network that Keploy and our application will use to communicate:

```bash
docker network create keploy-network
```

Next, start the MySQL instance using the provided `docker-compose.yml` file:

```bash
docker-compose up -d db
```

## Installation 📥

### With Docker 🎥

Build the application's Docker image:

```sh
docker build -t flask-mysql-app:1.0 .
```

Capture the test cases and mocks:

```shell
keploy record -c "docker run -p 5000:5000 --name flask-mysql-app --network keploy-network -e DB_HOST=db flask-mysql-app:1.0" --containerName flask-mysql-app
```

🔥**Make some API calls**. Postman, Hoppscotch or even curl - take your pick!

### Generate testcases

To generate test cases, we just need to **make some API calls.**

**1. Log in to get a JWT token**

First, we need to authenticate to get an access token. The default credentials are `admin` / `admin123`.

```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123"}' http://localhost:5000/login
```

This will return a token. Copy the `access_token` value and export it as an environment variable to make the next steps easier.

```bash
export JWT_TOKEN=<your_access_token_here>
```

**2. Create a new data payload**

```bash
curl -X POST \
  http://localhost:5000/data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"message": "First data log"}'
```

**3. Get all data payloads**

```bash
curl -X GET \
  http://localhost:5000/data \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**4. Get a financial summary report**

```bash
curl -X GET \
  http://localhost:5000/reports/full-financial-summary \
  -H "Authorization: Bearer $JWT_TOKEN"
```

Give yourself a pat on the back! With that simple spell, you've conjured up a test case with a mock! Explore the **Keploy directory** and you'll discover your handiwork in `test-1.yml` and `mocks.yml`.

A generated test case for the POST request will look like this:

```yaml
version: api.keploy.io/v1beta2
kind: Http
name: test-1
spec:
    metadata: {}
    req:
        method: POST
        proto_major: 1
        proto_minor: 1
        url: /data
        header:
            Accept: "*/*"
            Authorization: Bearer <your_jwt_token>
            Content-Length: "29"
            Content-Type: application/json
            Host: localhost:5000
            User-Agent: curl/7.81.0
        body: '{"message": "First data log"}'
        body_type: ""
        timestamp: 2023-12-01T10:00:00Z
    resp:
        status_code: 201
        header:
            Content-Length: "20"
            Content-Type: application/json
        body: |
            {"status":"created"}
        body_type: ""
        status_message: ""
        proto_major: 0
        proto_minor: 0
        timestamp: 2023-12-01T10:00:01Z
    objects: []
    assertions:
        noise:
            - header.Date
    created: 1701424801
curl: |-
    curl --request POST \
      --url http://localhost:5000/data \
      --header 'Host: localhost:5000' \
      --header 'User-Agent: curl/7.81.0' \
      --header 'Authorization: Bearer <your_jwt_token>' \
      --header 'Accept: */*' \
      --header 'Content-Type: application/json' \
      --data '{"message": "First data log"}'
```

This is how the captured MySQL dependency in `mocks.yml` would look:

```yaml
version: api.keploy.io/v1beta2
kind: MySql
name: mocks
spec:
    metadata:
      name: payloads
      type: TABLE
      operation: query
    requests:
        - header:
            header:
                payload_length: 39
                sequence_id: 1
                packet_type: COM_QUERY
          message:
            query: "INSERT INTO payloads (data) VALUES ('First data log')"
    responses:
        - header:
            header:
                payload_length: 9
                sequence_id: 2
            packet_type: OK
          message:
            header: 0
            affected_rows: 1
            last_insert_id: 5
    created: 1701424801
```

Want to see if everything works as expected?

#### Run Tests

Time to put things to the test 🧪

```shell
keploy test -c "docker run -p 5000:5000 --name flask-mysql-app --network keploy-network -e DB_HOST=db flask-mysql-app:1.0" --delay 10 --containerName flask-mysql-app
```

> The `--delay` flag? Oh, that's just giving your app a little breather (in seconds) before the test cases come knocking.

---

### Running In Linux/WSL

We'll be running our sample application right on Linux, but we'll keep the MySQL database running in Docker as set up earlier. Ready? Let's get the party started!🎉

#### 📼 Roll the Tape - Recording Time!

First, install the Python dependencies:

```bash
pip install -r requirements.txt
```

Before running, ensure the `DB_HOST` environment variable points to your Docker database instance, which is exposed on `127.0.0.1`.

```bash
export DB_HOST=127.0.0.1
```

Ready, set, record! Here's how:

```bash
keploy record -c "python3 main.py"
```

Keep an eye out for the `-c` flag! It's the command charm to run the app.

Alright, magician! With the app alive and kicking, let's weave some test cases. The spell? Making the same API calls as before!

#### Generate testcases

**1. Log in to get a JWT token**

```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123"}' http://localhost:5000/login
# Export the token
export JWT_TOKEN=<your_access_token_here>
```

**2. Create a new data payload**

```bash
curl -X POST \
  http://localhost:5000/data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"message": "First data log"}'
```

**3. Get all data payloads**

```bash
curl -X GET \
  http://localhost:5000/data \
  -H "Authorization: Bearer $JWT_TOKEN"
```

After making a few calls, you will see test cases and mocks being generated in your project directory.

#### Run Tests

Time to put things to the test 🧪

```shell
keploy test -c "python3 main.py" --delay 10
```

Final thoughts? Dive deeper! Try different API calls, tweak the DB response in the `mocks.yml`, or fiddle with the request or response in `test-x.yml`. Run the tests again and see the magic unfold!✨👩‍💻👨‍💻✨

## Wrapping it up 🎉

Congrats on the journey so far! You've seen Keploy's power, flexed your coding muscles, and had a bit of fun too! Now, go out there and keep exploring, innovating, and creating! Remember, with the right tools and a sprinkle of fun, anything's possible. 😊🚀

Happy coding! ✨👩‍💻👨‍💻✨