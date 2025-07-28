# Use official Python base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app code
COPY . .

# Expose the port
ENV PORT=5000

# Start with gunicorn
CMD ["gunicorn", "-b", ":5000", "app:app"]
