# Use the official Python image as the base image
FROM python:3.11.5-bullseye

# Install PostgreSQL client
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
	postgresql-client \
    curl \
    netcat-traditional

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables for PostgreSQL
# ENV POSTGRES_USER=postgres \
#     POSTGRES_PASSWORD=postgres \
#     POSTGRES_DB=studentdb \
#     POSTGRES_HOST=0.0.0.0 \
#     POSTGRES_PORT=5432

# Expose port 80 for the FastAPI application
EXPOSE 8000

# Start the FastAPI application
CMD [ "/app/entrypoint.sh" ]
