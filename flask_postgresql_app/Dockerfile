
FROM python:3.9-slim


WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents 
COPY . .

EXPOSE 5000

# env
ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0"]
