To run the application, you need [docker](https://docs.docker.com/get-docker/) installed in your system.

Once docker is installed, run the following commands - ```docker-compose build``` and ```docker-compose up``` to start the server.
The Django application container will be accessible at port 8000 and at url - `https://127.0.0.1:8000` whereas locally, PostgreSQL will be accessible at port 6000 and at port 5432 in the container.

To apply migrations, run the following commands - ```docker-compose exec web /bin/sh``` which opens a command input to the container and now run - ```python3 manage.py makemigrations``` and ```python3 manage.py migrate```.

Make the following requests to the respective endpoints -  

1. `GET /user/` - To get all the data at once.
2. `GET /user/uuid/` - To get the data of any particular user.
3. `POST /user/` - To create a new user.
4. `PUT /user/uuid/` - To update an existing user.
5. `DELETE /user/uuid/` - To delete an existing user.

The User model has the following fields -  

1. id - UUID Field
2. name - String Field
3. email - Email Field
4. password - String Field
5. website - String Field

Pick up the data from `data.json` file to perform CRUD operation.
