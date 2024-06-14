# Use the official Python image as the base image
FROM python:3.10.12

# Set the working directory within the container
WORKDIR /app

# Copy the application code into the container
COPY . .

# Install the required packages
RUN pip3 install -r requirements.txt

# Expose the port that the Flask app will run on
EXPOSE 5000

# Start the Flask application
CMD ["python3", "app.py"]
