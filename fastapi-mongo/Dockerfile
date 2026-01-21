# 1. Use a lightweight Python 3.10 image
FROM python:3.10-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set working directory
WORKDIR /app

# 4. Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements.txt from the root folder
COPY ../requirements.txt .

# 6. Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# 7. Copy everything from quizzly folder (backend code)
COPY . .

# 8. Expose port
EXPOSE 8000

# 9. Run FastAPI app with uvicorn
CMD ["uvicorn", "quizzly.main:app", "--host", "0.0.0.0", "--port", "8000"]
