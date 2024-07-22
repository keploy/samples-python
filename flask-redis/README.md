# Keploy

## Introduction
This is a simple to-do application built using Python's Flask Framework and Redis. It supports all CRUD operations on the to-do items through a RESTful API.

Here's all the supported endpoints.
Sure, here's the information organized into a markdown table, including the payload details:

## API Endpoints

| Method | Endpoint | Payload | Description |
|---|---|---|---|
| GET | / |  None | Check the status of the application. |
| GET | /todos | None | Gets all to-dos. |
| GET | /todos/{id} | None | Gets the to-do with the specified id. |
| POST | /todos | `{ "title": "required, "description": "optional" }` | Creates a new to-do.                     |
| PUT | /todos/{id} | `{ "title": "optional", "description": "optional" }` | Updates the to-do with the given id. Throws error if it does not exist. |
| DELETE | /todos/{id} | None | Deletes the to-do with the given id. |

## Setup Without Docker

First install the dependencies.

```bash
git clone https://github.com/keploy/samples-python.git && cd samples-python/flask-redis
pip3 install -r requirements.txt
```

To run the application, use the following command.

```bash
gunicorn --config gunicorn_config.py app:app
```

This will start your server at `https://localhost:3000`.

## Setup With Docker

If you docker installed, simply run `docker compose up` and it will start your server.

Make sure you have provided all the environment variables in `.env` file.

Head over to `https://localhost:3000` in your browser to check if everything is working.

## Install Keploy

Keploy can be installed on Linux directly. If you're on windows, you would need Windows Subsystem For Linux (WSL). Based on your system architecture, install the keploy latest binary release. Read more about it [here](https://keploy.io/docs/server/installation/).

### For Linux, MacOS and WSL
Create a bridge network in Docker using the following docker network create command.
```bash
docker network create keploy-network
```

Run the following command to start the Keploy container.
```bash
alias keploy="docker run --name keploy-v2 -p 16789:16789 --network keploy-network --privileged --pid=host -v $(pwd):$(pwd) -w $(pwd) -v /sys/fs/cgroup:/sys/fs/cgroup -v /sys/kernel/debug:/sys/kernel/debug -v /sys/fs/bpf:/sys/fs/bpf -v /var/run/docker.sock:/var/run/docker.sock --rm ghcr.io/keploy/keploy"
```

## Recording API Calls

Run the following command to start recording your API calls.

```bash
keploy record -c "gunicorn --config gunicorn_config.py app:app"
```

If you're using docker then use this command.
```bash
keploy record -c "docker compose up"
```

Now, you can start making API calls using your preferred client like curl or postman. Keploy will record these calls and generate test-cases and mocks from these API calls.

Let's make some sample API requests.

```bash
curl --location 'http://127.0.0.1:3000/todos/' \
--header 'Content-Type: application/json' \
--data-raw '    {
        "title": "Example TODO 01",
        "description": "An Example TODO",
    }'
```
```bash
curl --location 'http://127.0.0.1:3000/todos/' \
--header 'Content-Type: application/json' \
--data-raw '    {
        "title": "Example TODO 02"
    }'
```
```bash
curl --location 'http://127.0.0.1:8000/todos/'
```
Make some more requests like PUT, DELETE, etc.

## Replay Recorded Testcases
Once you're done, you can replay the test cases using the following commands.

```bash
keploy test -c "gunicorn --config gunicorn_config.py app:app" --delay 20
```