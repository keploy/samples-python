FROM python:3.11.5-bullseye

# Set working directory
WORKDIR /app


# Copy all files
COPY . /app/


# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


# Install system CA certificates (Debian-based)
RUN apt-get update && apt-get install -y ca-certificates curl && rm -rf /var/lib/apt/lists/*


# Download Keploy CA and setup script
ADD https://raw.githubusercontent.com/keploy/keploy/refs/heads/main/pkg/core/proxy/tls/asset/ca.crt ca.crt
ADD https://raw.githubusercontent.com/keploy/keploy/refs/heads/main/pkg/core/proxy/tls/asset/setup_ca.sh setup_ca.sh


# Make the script executable
RUN chmod +x setup_ca.sh

# Expose FastAPI port
EXPOSE 8000

# Run the Keploy CA setup script and then start FastAPI
CMD ["/bin/bash", "-c", "source ./setup_ca.sh && uvicorn main:app --host 0.0.0.0 --port 8000"]
