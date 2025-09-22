import aiohttp
import asyncio
import random

async def send_kafka_message(session, message_id):
    url = "http://34.131.193.34:5000/send-kafka"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "no": message_id,
        "type": "test",
        "content": f"bro you are best #{message_id}",
        "topic": "notification-topic",
        "partition": 1
    }

    async with session.post(url, json=payload, headers=headers) as response:
        resp_text = await response.text()
        print(f"[{message_id}] Status: {response.status}, Response: {resp_text}")

async def main():
    async with aiohttp.ClientSession() as session:
        for i in range(1, 200):  # Send 5 messages
            await send_kafka_message(session, i)
            await asyncio.sleep(1)  # wait 1 second between messages

# Run the loop
asyncio.run(main())
