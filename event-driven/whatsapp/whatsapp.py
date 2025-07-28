from twilio.rest import Client
import os
import requests
import json
from flask import Flask, request
app = Flask(__name__)


ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_WHATSAPP = os.getenv("TWILIO_FROM_WHATSAPP")

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)
def send(to_number, body):
    try:
        msg = twilio_client.messages.create(
            body=body,
            from_=FROM_WHATSAPP,
            to=f'whatsapp:+91{to_number}'
        )
        print(f"✅ Sent WhatsApp to {to_number}: SID {msg.sid}")
    except Exception as e:
        print(f"❌ Failed to send WhatsApp to {to_number}: {e}")
        
@app.route('/send', methods=['POST'])
def send_whatsapp():
    send_data = request.json
    to_number = send_data.get('to')
    body = send_data.get('body')
    if not to_number or not body:
        return {"error": "Missing 'to' or 'body' in request"}, 400
    send(to_number, body)
    return {"status": "Message sent successfully"}, 200 

if __name__ == '__main__':
    app.run(host="0.0.0", port=5000, debug=False)
