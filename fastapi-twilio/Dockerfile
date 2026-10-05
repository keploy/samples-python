FROM python:3.11.5-bullseye

# Set working directory
WORKDIR /app


# Copy all files
COPY . /app/


# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


# Install system CA certificates (Debian-based). Keploy injects its per-run MITM
# CA and the trust env vars automatically, so no certificate is baked in here.
RUN apt-get update && apt-get install -y ca-certificates curl && rm -rf /var/lib/apt/lists/*

# Expose FastAPI port
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
