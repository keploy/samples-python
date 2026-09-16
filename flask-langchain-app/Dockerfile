# Use official Python image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies for python-magic and pymupdf
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    mupdf-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
COPY . .

# Create uploads directory
RUN mkdir -p static/uploads

# Expose port
EXPOSE 5000

# Run the app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"] 