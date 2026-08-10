# Set base image
FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create and set the working directory
ARG HOST_PWD
WORKDIR $HOST_PWD

# Install dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy the project files
COPY . .

# Run migrations and start the server with proper signal handling

# FOR RECORD MODE
ENTRYPOINT ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && exec python manage.py runserver 0.0.0.0:8000"]

# FOR TEST MODE
# ENTRYPOINT ["sh", "-c", "exec python -m coverage run manage.py runserver 0.0.0.0:8000 --noreload"]