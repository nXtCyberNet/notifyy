FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fcm/app.py .

EXPOSE 5003 8003

CMD ["python", "app.py"]
