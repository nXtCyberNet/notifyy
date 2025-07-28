import requests
import json

PRODUCER_URL = "http://34.131.193.34:5000/send-kafka"  # Replace with your actual URL

headers = {"Content-Type": "application/json"}

prom = """commerce
🎉 Big Sale Alert!

Get up to 40% OFF on our bestsellers — only for the next 48 hours! 🛒🔥

🧼 Skincare | 👕 Fashion | 🎧 Gadgets — everything you love, now at unbeatable prices.

🛍️ Shop now: [your-link]
💬 Need help? Just reply “Order” and we’ll assist you instantly!

"""

email_prom = """ Hi sir 

Ready to take your productivity to the next level?

Meet nothing.ai  – the smart way to manage tasks teams and timelines all in one place. Whether you're a freelancer team leader or startup founder, [YourProduct] helps you stay focused, organized, and ahead of the curve.

✅ Easy project tracking
✅ Real-time collaboration
✅ Powerful analytics
✅ 100% cloud-based & secure

Try it free for 14 days – no credit card required.
👉 [Start My Free Trial]

Thousands of users have already streamlined their workflows using [YourProduct]. Why not join them?

Have questions? Just reply to this email — we're here to help!

Cheers



"""



# 1. Send Email Notification (order type)
email_payload = {
    "no": 1,
    "type": "order",
    "content": "Your order #1298 has been placed successfully!",
    "topic": "email-topic",
    "partition": 0
}

email_payload2 = {
    "no": 1,
    "type": "prom",
    "content": email_prom,
    "topic": "email-topic",
    "partition": 0
}

# 2. Send WhatsApp Notification
whatsapp_payload = {
    "no": 1,
    "type": "whatsapp",
    "content": prom ,
    "topic": "notification-topic",
    "partition": 0
}

# 3. Send Push Notification
push_payload = {
    "no": 3,
    "type": "push",
    "content": "🔥 Limited time offer! 20% off on all electronics.",
    "topic": "notification-topic",
    "partition": 0
}

# 4. Benchmark/Test Logging
benchmark_payload = {
    "no": 4,
    "type": "benchmark",
    "content": "Log this message for testing system metrics-1234",
    "topic": "notification-topic",
    "partition": 1
}


def send_payload(payload):
    response = requests.post(PRODUCER_URL, headers=headers, data=json.dumps(payload))
    print(f"Sent: {payload['type']} | Status: {response.status_code} | Response: {response.text}")


if __name__ == "__main__":
    send_payload(email_payload)
    
    
    send_payload(whatsapp_payload)
    send_payload(push_payload)
    for i in range(10):
        
        send_payload(benchmark_payload)
        
        
