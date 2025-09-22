import asyncio

from confluent_kafka import Consumer
import asyncpg
from aiosmtplib import SMTP
from email.mime.text import MIMEText
import os 

from prometheus_client import start_http_server, Counter


EMAILS_SENT_COUNTER = Counter('emails_sent_total', 'Number of emails sent')


start_http_server(8000)


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
# Email credentials
sender = "alaotach@gmail.com"
password = "ayrh omvs mcsy kvdc"  # Use Gmail App Password, not normal password
server = os.getenv("server")# Kafka config
conf = {
    'bootstrap.servers': server ,
    'group.id': 'email_group',
    'auto.offset.reset': 'earliest',
}

# PostgreSQL connection
async def pg_con():
    return await asyncpg.connect(
        host=PG_HOST,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )

# Get email for order
async def get_email(conn, order_id):
    row = await conn.fetchrow("SELECT email FROM info WHERE orderid = $1", order_id)
    if row:
        return row["email"]
    raise ValueError("Email not found for order.")

# Get promotional email list
async def get_promotional_emails(conn):
    rows = await conn.fetch("SELECT email FROM info")
    return [row["email"] for row in rows]

# Send an email
async def send_email(receiver, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver
    try:
        smtp = SMTP(hostname="smtp.gmail.com", port=465, use_tls=True)
        await smtp.connect()
        await smtp.login(sender, password)
        await smtp.send_message(msg)
        await smtp.quit()

        # Increment the Prometheus counter for every successful email send.
        EMAILS_SENT_COUNTER.inc()
        print(f"✅ Sent email to {receiver}")
    except Exception as e:
        print(f"❌ Failed to send email to {receiver}: {e}")

# Kafka consumer loop
async def consume_loop():
    conn = await pg_con()
    consumer = Consumer(conf)
    consumer.subscribe(['email-topic'])
    loop = asyncio.get_running_loop()

    try:
        while True:
            msg = await loop.run_in_executor(None, consumer.poll, 1.0)
            if msg is None:
                await asyncio.sleep(0.1)
                continue
            if msg.error():
                print("Consumer error:", msg.error())
                continue

            mssg = msg.value().decode('utf-8')
            print(f"📩 Received message: {mssg}")

            try:
                parts = mssg.split(',')
                order_id = int(parts[0])
                types = parts[1].strip()
                content = parts[2].strip()

                if types == "prom":
                    email_list = await get_promotional_emails(conn)
                    tasks = [send_email(email, "Promotion", content) for email in email_list]
                    await asyncio.gather(*tasks)
                if types == "order":
                    receiver = await get_email(conn, order_id)
                    subject = "Order Update"
                    body = f"Order ID: {order_id}\nContent: {content}"
                    await send_email(receiver, subject, body)
                else:
                    print("test message")
            except Exception as e:
                print(f"⚠️ Failed to process message: {e}")

            await asyncio.sleep(0.1)
    finally:
        consumer.close()
        await conn.close()

# Main runner
async def main():
    await consume_loop()

asyncio.run(main())