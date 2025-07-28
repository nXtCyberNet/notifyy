#!/usr/bin/env python3
"""
WhatsApp Microservice
Handles WhatsApp notifications via Twilio
"""

from flask import Flask, request, jsonify
import os
import logging
from twilio.rest import Client
from prometheus_client import Counter, Histogram, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
WHATSAPP_SENT = Counter('whatsapp_sent_total', 'Total WhatsApp messages sent', ['status'])
WHATSAPP_PROCESSING_TIME = Histogram('whatsapp_processing_seconds', 'Time spent processing WhatsApp messages')

# Twilio credentials from environment variables
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'your_account_sid')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'your_auth_token')
FROM_WHATSAPP = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

# Initialize Twilio client
twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_whatsapp_message(to_number, message):
    """Send WhatsApp message via Twilio"""
    try:
        # Format phone number for WhatsApp
        if not to_number.startswith('whatsapp:'):
            if not to_number.startswith('+'):
                to_number = f'+91{to_number}'  # Default to India country code
            to_number = f'whatsapp:{to_number}'
        
        message = twilio_client.messages.create(
            body=message,
            from_=FROM_WHATSAPP,
            to=to_number
        )
        
        logger.info(f"✅ WhatsApp sent to {to_number}, SID: {message.sid}")
        WHATSAPP_SENT.labels(status='success').inc()
        return message.sid
        
    except Exception as e:
        logger.error(f"❌ Failed to send WhatsApp to {to_number}: {e}")
        WHATSAPP_SENT.labels(status='failure').inc()
        raise

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "whatsapp"})

@app.route('/send-whatsapp', methods=['POST'])
def send_whatsapp_endpoint():
    """Send WhatsApp message endpoint"""
    with WHATSAPP_PROCESSING_TIME.time():
        try:
            data = request.json
            
            # Extract data
            phone = data.get('phone')
            message = data.get('message', '')
            title = data.get('title', 'Notification')
            user_id = data.get('user_id')
            
            if not phone:
                return jsonify({"error": "Phone number is required"}), 400
            
            if not message:
                return jsonify({"error": "Message content is required"}), 400
            
            # Combine title and message
            full_message = f"*{title}*\n\n{message}"
            
            # Send WhatsApp message
            message_sid = send_whatsapp_message(phone, full_message)
            
            return jsonify({
                "status": "success",
                "message": "WhatsApp sent successfully",
                "user_id": user_id,
                "phone": phone,
                "message_sid": message_sid
            })
            
        except Exception as e:
            logger.error(f"Error in WhatsApp endpoint: {e}")
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start Prometheus metrics server
    start_http_server(8002)
    logger.info("📊 WhatsApp service metrics available at http://localhost:8002")
    
    logger.info("🚀 Starting WhatsApp Microservice on port 5002")
    app.run(host="0.0.0.0", port=5002, debug=False)
