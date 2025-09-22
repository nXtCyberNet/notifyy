FROM python:3.9-bullseye
# Set environment variables 
WORKDIR /app
COPY  requirements.txt .
RUN pip install -r requirements.txt
COPY . .


CMD ["python" , "main.py"]
