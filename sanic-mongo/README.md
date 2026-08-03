This application is a simple movie management API built using Python's Sanic framework and MongoDB for data storage. It allows you to perform basic CRUD (Create, Read, Update, Delete) operations on Movie records.

## Table of Contents

# Introduction

🪄 Dive into the world of Movie CRUD Apps and see how seamlessly Keploy integrated with [Sanic](hhttps://sanic.dev/en/) and [MongoDB](https://www.mongodb.com/). Buckle up, it's gonna be a fun ride! 🎢

## Pre-Requisite 🛠️

- Install WSL (`wsl --install`) for <img src="https://keploy.io/docs/img/os/windows.png" alt="Windows" width="3%" /> Windows.

## Optional 🛠️

- Install Colima( `brew install colima && colima start` ) for <img src="https://keploy.io/docs/img/os/macos.png" alt="MacOS" width="3%" /> MacOs.

## Installation 📥

Depending on your OS, choose your adventure:

Alright, let's equip ourselves with the **latest Keploy binary**:

```bash
curl --silent --location "https://github.com/keploy/keploy/releases/latest/download/keploy_linux_amd64.tar.gz" | tar xz -C /tmp

sudo mkdir -p /usr/local/bin && sudo mv /tmp/keploy /usr/local/bin && keploy
```

#### Add alias for Keploy:

```bash
alias keploy='sudo docker run --pull always --name keploy-v2 -p 16789:16789 --privileged --pid=host -it -v "$(pwd)":/files -v /sys/fs/cgroup:/sys/fs/cgroup -v /sys/kernel/debug:/sys/kernel/debug -v /sys/fs/bpf:/sys/fs/bpf -v /var/run/docker.sock:/var/run/docker.sock -v '"$HOME"'/.keploy-config:/root/.keploy-config -v '"$HOME"'/.keploy:/root/.keploy --rm ghcr.io/keploy/keploy'
```

Now head to the folder of the application and run

1. Navigate your project directory:

    ```bash
    cd sample-python/sanic-mongo
    ```

2. Create a Virtual Environment:

    ```bash
    python -m venv venv
    ```
3. Activating the Virtual Environment

    On Windows:

    ```bash
    venv\Scripts\activate
    ```

    On macOS and Linux:

    ```bash
    source venv/bin/activate
    ```
4. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```
5. To exit your Virtual Environment:

    ```bash
    deactivate
    ```

### Lights, Camera, Record! 🎥

Capture the test-cases-

```shell
keploy record -c "python3 server.py"
```

🔥**Make some API calls**. Postman, Hoppscotch or even curl - take your pick!

Let's make URLs short and sweet:

### Generate testcases

To generate testcases we just need to **make some API calls.**

**1. Make a POST requests**

```bash
  curl -X "POST" "http://127.0.0.1:8000/add_movie" \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json; charset=utf-8' \
    -d '{
        "name": "Whiplash"
    }'
```

```bash
  curl -X "POST" "http://127.0.0.1:8000/add_movie" \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json; charset=utf-8' \
    -d '{
        "name": "Chappie"
    }'
```

```bash
  curl -X "POST" "http://127.0.0.1:8000/add_movie" \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json; charset=utf-8' \
    -d '{
        "name": "Titanic"
    }'
```

**2. Make a GET request**

In order to see all the movies added to the database, run:

```
curl -X "GET" "http://127.0.0.1:8000/movies" \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json; charset=utf-8'
```

**3. Make a DELETE request**

In order to delete all the movies, run:

```bash
  curl -X "DELETE" "http://127.0.0.1:8000/movies" \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json; charset=utf-8'
```

You will now see a folder named `keploy` with your recorded tests.

#### Run Tests

Time to put things to the test 🧪

```shell
keploy test -c "python server.py"
```

## Wrapping it up 🎉

Congrats on the journey so far! You've seen Keploy's power, flexed your coding muscles, and had a bit of fun too! Now, go out there and keep exploring, innovating, and creating! Remember, with the right tools and a sprinkle of fun, anything's possible.😊🚀

Happy coding! ✨👩‍💻👨‍💻✨

<br/>
