from flask import Flask, request
import asyncpg
import asyncio
from flask_cors import CORS
from confluent_kafka import Producer
import json
import os 

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "root",
    "host": "34.131.223.3",
    "port": 5432
}
PG_HOST = DB_CONFIG["host"]
PG_DB = DB_CONFIG["dbname"]
PG_USER = DB_CONFIG["user"]
PG_PASSWORD = DB_CONFIG["password"]

# Kafka configuration
bootstrap_servers = os.getenv("SERVER")  # e.g. "localhost:9092"

# Initialize confluent_kafka Producer
producer = Producer({
    "bootstrap.servers": bootstrap_servers
})

async def pg_con():
    return await asyncpg.connect(
        host=PG_HOST,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )

async def save_token(token, orderid):
    conn = await pg_con()
    await conn.execute(
        "UPDATE info SET fmc_token = $1 WHERE orderid = $2",
        token, orderid
    )
    await conn.close()

@app.route('/register-token', methods=['POST'])
def register_token():
    data = request.get_json()
    token = data.get('token')
    orderid = data.get('orderid')
    print(f"Received token: {token[:10]}...{token[-5:]} for orderid {orderid}")
    if token:
        asyncio.run(save_token(token, orderid if orderid else 1))
        return {'status': 'success'}, 200
    return {'status': 'error', 'message': 'No token provided'}, 400

@app.route('/send-kafka', methods=['POST'])
def send_kafka():
    """
    Expects JSON body:
    {
        "no": <number>,
        "type": <string>,
        "content": <string>,
        "topic": <string>,
        "partition": <integer>
    }
    """
    data = request.get_json()
    no = data.get('no')
    type_ = data.get('type')
    content = data.get('content')
    topic = data.get('topic')
    partition = data.get('partition')

    # Validate required fields
    if any(v is None for v in [no, type_, content, topic, partition]):
        return {
            "status": "error",
            "message": "Fields 'no', 'type', 'content', 'topic', and 'partition' are required."
        }, 400

    # Construct message
    message = f"{no},{type_},{content}"

    try:
        # Specify topic and partition in produce
        producer.produce(
            topic=topic,
            value=message.encode("utf-8"),
            partition=partition
        )
        producer.flush()
        return {"status": "success", "message": f"Message sent to topic '{topic}' on partition {partition}."}, 200
    except Exception as e:
        return {"status": "error", "message": f"Kafka send failed: {str(e)}"}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)