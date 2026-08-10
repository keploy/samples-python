# Define an argument for the Debian version with a default value
# This allows you to build for a specific version, e.g., bullseye, bookworm, or trixie
ARG DEBIAN_VERSION=bookworm

# Use the argument in the FROM instruction
FROM python:3.9-slim-${DEBIAN_VERSION}

# --- DNS/NSS fix (bullseye-slim often lacks these) ---
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        libnss-dns libnss-files netbase ca-certificates && \
    rm -rf /var/lib/apt/lists/*; \
    # Ensure glibc actually consults DNS
    if ! grep -q '^hosts:.*\bdns\b' /etc/nsswitch.conf 2>/dev/null; then \
        echo 'hosts: files dns' > /etc/nsswitch.conf; \
    fi

# Set the working directory
WORKDIR /app

# Create a non-root user to run the application
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy the requirements file and install dependencies
# This is done first to leverage Docker's layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the port that the Flask app will run on
EXPOSE 6000

# Start the Flask application
CMD ["python3", "app.py"]
