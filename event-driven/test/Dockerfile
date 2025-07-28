FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY test/app.py .

EXPOSE 5004 8004

CMD ["python", "app.py"]
