# User Data CRUD Application

A sample user data CRUD app to test Keploy integration capabilities using [Django](https://www.djangoproject.com/) and [PostgreSQL](https://www.postgresql.org/). <br>
Make the following requests to the respective endpoints -  

1. `GET /user/` - To get all the data at once.
2. `GET /user/uuid/` - To get the data of any particular user.
3. `POST /user/` - To create a new user.
4. `PUT /user/uuid/` - To update an existing user.
5. `DELETE /user/uuid/` - To delete an existing user.

## Installation Setup

```bash
git clone https://github.com/keploy/samples-python.git && cd samples-python/django-postgres/django_postgres
```

## Installation Keploy

Keploy can be installed on Linux directly and on Windows with the help of WSL. Based on your system architecture, install the keploy latest binary release

```bash
 curl -O https://keploy.io/install.sh && source install.sh
 keploy
```

### Starting the PostgreSQL Instance

```bash
# Start the application
docker-compose up -d
```

### Setting Django Application

This is a one time setup of django application.

```bash
python3 -m virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
```

### Capture the Testcases

This command will start the recording of API calls using ebpf:-

```shell
sudo -E keploy record -c "python3 manage.py runserver"
```

Make API Calls using Hoppscotch, Postman or cURL command. Keploy with capture those calls to generate the test-suites containing testcases and data mocks.

### Generate testcases

To generate testcases we just need to make some API calls. You can use [Postman](https://www.postman.com/), [Hoppscotch](https://hoppscotch.io/), or simply `curl`

### Make a POST request

```bash
curl --location 'http://127.0.0.1:8000/user/' \
--header 'Content-Type: application/json' \
--data-raw '    {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "password": "smith567",
        "website": "www.janesmith.com"
    }'
```

```bash
curl --location 'http://127.0.0.1:8000/user/' \
--header 'Content-Type: application/json' \
--data-raw '    {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "john567",
        "website": "www.johndoe.com"
    }'
```

### Make a GET request to get all the data

```bash
curl --location 'http://127.0.0.1:8000/user/'
```

This will return all the data saved in the database.

### Make a GET request to get a specific data

```bash
curl --location 'http://127.0.0.1:8000/user/<USER_ID>'
```

### Make a PUT request to update a specific data

```bash
curl --location --request PUT 'http://127.0.0.1:8000/user/<USER_ID>' \
--header 'Content-Type: application/json' \
--data-raw '    {
        "name": "Jane Smith",
        "email": "smith.jane@example.com",
        "password": "smith567",
        "website": "www.smithjane.com"
    }'
```

### Make a DELETE request to delete a specific data

```bash
curl --location --request DELETE 'http://127.0.0.1:8000/user/<USER_ID>'
```

Now both these API calls were captured as **editable** testcases and written to `keploy/tests` folder. The keploy directory would also have `mocks` file that contains all the outputs of postgres operations.

## Run the Testcases

Now let's run the application in test mode.

```shell
sudo -E keploy test -c "python3 manage.py runserver" --delay 10
```

So, no need to setup fake database/apis like Postgres or write mocks for them. Keploy automatically mocks them and, **The application thinks it's talking to Postgres 😄**
