# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# ---- START NEW ----
# Explicitly create the directory for sockets to ensure it exists
# with the correct permissions before the volume is mounted over it.
RUN mkdir -p /keploy-sockets && chmod 777 /keploy-sockets
# ---- END NEW ----


# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Create the keploy directory and download the time freeze agent
RUN mkdir -p /lib/keploy
ADD https://keploy-enterprise.s3.us-west-2.amazonaws.com/releases/latest/assets/freeze_time_amd64.so /lib/keploy/freeze_time_amd64.so
RUN chmod +x /lib/keploy/freeze_time_amd64.so
RUN ls -la /lib/keploy/freeze_time_amd64.so

# Set LD_PRELOAD environment variable
ENV LD_PRELOAD=/lib/keploy/freeze_time_amd64.so
ENV FLASK_ENV=production

# Expose port 5000 for Flask
EXPOSE 5000

# ---- START NEW HEALTHCHECK ----
# Add a healthcheck to ensure the app is running before considering it "up"
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1
# ---- END NEW HEALTHCHECK ----

CMD ["python", "main.py"]