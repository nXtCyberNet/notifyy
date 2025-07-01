import asyncio
import asyncpg
import json
import time
import os
from confluent_kafka import Consumer , TopicPartition

from twilio.rest import Client
# Add Prometheus client import
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Initialize Prometheus metrics
MESSAGES_RECEIVED = Counter('whatsapp_messages_received_total', 
                          'Total number of WhatsApp notification messages received')
WHATSAPP_SENT = Counter('whatsapp_sent_total', 
                      'Total number of WhatsApp messages sent', 
                      ['status'])  # status: success, failure
WHATSAPP_PROCESSING_TIME = Histogram('whatsapp_processing_seconds', 
                                   'Time spent processing WhatsApp notifications')
DB_ERRORS = Counter('whatsapp_db_errors_total', 
                  'Total number of database errors')
MISSING_PHONE = Counter('whatsapp_missing_phone_total', 
                      'Count of missing phone numbers')
DB_QUERY_TIME = Histogram('whatsapp_db_query_seconds',
                        'Time spent on database queries')
KAFKA_CONSUMER_LAG = Gauge('whatsapp_kafka_consumer_lag',
                         'Kafka consumer lag in messages')

# Twilio Credentials
ACCOUNT_SID = 'AC46839eb2abc194085f1f293b36549d0c'
AUTH_TOKEN = '165492193b7dd4e17f859ffb1c51a2fa'
FROM_WHATSAPP = 'whatsapp:+14155238886'

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

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
server = os.getenv("SERVER")

conf = {
    'bootstrap.servers': server,
    'group.id': 'whatsapp_group',
    'auto.offset.reset': 'earliest',
}

async def pg_con(): 
    try:
        return await asyncpg.connect(
            host=PG_HOST,
            database=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
    except Exception as e:
        DB_ERRORS.inc()
        print(f"❌ Database connection error: {e}")
        raise

async def get_user_phone(conn, user_id):
    start_time = time.time()
    try:
        row = await conn.fetchrow("SELECT phone_no FROM info WHERE orderid = $1", user_id)
        if row:
            return row['phone_no']
        MISSING_PHONE.inc()
        raise ValueError("Phone number not found.")
    except ValueError:
        # Re-raise the ValueError for specific handling
        raise
    except Exception as e:
        DB_ERRORS.inc()
        print(f"❌ Database query error: {e}")
        raise
    finally:
        DB_QUERY_TIME.observe(time.time() - start_time)

def send(to_number, body):
    try:
        msg = twilio_client.messages.create(
            body=body,
            from_=FROM_WHATSAPP,
            to=f'whatsapp:+91{to_number}'
        )
        WHATSAPP_SENT.labels(status="success").inc()
        print(f"✅ Sent WhatsApp to {to_number}: SID {msg.sid}")
    except Exception as e:
        WHATSAPP_SENT.labels(status="failure").inc()
        print(f"❌ Failed to send WhatsApp to {to_number}: {e}")

async def kafka_consumer():
    conn = await pg_con()
    consumer = Consumer(conf)
    consumer.assign([TopicPartition('notification-topic', 0)])
    loop = asyncio.get_running_loop()
    try:
        while True:
            msg = await loop.run_in_executor(None, consumer.poll, 1.0)
            if msg is None:
                await asyncio.sleep(0.1)
                continue
            if msg.error():
                print("❌ Kafka error:", msg.error())
                continue
            
            # Record message received
            MESSAGES_RECEIVED.inc()
            
            # Use histogram to track processing time
            start_time = time.time()
            
            try:
                mssg = msg.value().decode('utf-8')
                parts = mssg.split(',')
                order_id = int(parts[0])
                types = parts[1].strip()
                content = parts[2].strip()
                if types != 'prom':
                    phone = await get_user_phone(conn, order_id)
                    send(phone, content)
            except ValueError as e:
                # Specific handling for phone number not found
                print(f"⚠️ {e}")
            except Exception as e:
                print(f"⚠️ Processing error: {e}")
            finally:
                # Record the time taken to process the message
                WHATSAPP_PROCESSING_TIME.observe(time.time() - start_time)
    finally:
        consumer.close()
        await conn.close() 
        
async def main():
    # Start Prometheus HTTP server on port 8000
    start_http_server(8000)
    await kafka_consumer()

if __name__ == '__main__':
    asyncio.run(main())