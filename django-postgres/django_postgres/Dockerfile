# Use an official Python runtime as a parent image
FROM python:3.11.7-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y libpq-dev

# Create and set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of your application code into the container
COPY . /app/

# Expose the port your application runs on
EXPOSE 8000

# Define the command to run your application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

