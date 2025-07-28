#!/usr/bin/env python3
"""
FCM (Firebase Cloud Messaging) Microservice
Handles push notifications via Firebase
"""

from flask import Flask, request, jsonify
import os
import logging
import asyncio
from firebase_admin import credentials, messaging, initialize_app
from prometheus_client import Counter, Histogram, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
FCM_SENT = Counter('fcm_sent_total', 'Total FCM messages sent', ['status'])
FCM_PROCESSING_TIME = Histogram('fcm_processing_seconds', 'Time spent processing FCM messages')

# Initialize Firebase Admin SDK
try:
    firebase_creds_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "credentials.json")
    if os.path.exists(firebase_creds_path):
        cred = credentials.Certificate(firebase_creds_path)
        initialize_app(cred)
        logger.info("✅ Firebase Admin SDK initialized")
    else:
        logger.warning("⚠️ Firebase credentials file not found")
except Exception as e:
    logger.error(f"❌ Failed to initialize Firebase: {e}")

def send_fcm_notification(fcm_token, title, message, data=None):
    """Send FCM notification"""
    try:
        # Create message
        fcm_message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message,
            ),
            data=data or {},
            token=fcm_token,
        )
        
        # Send message
        response = messaging.send(fcm_message)
        logger.info(f"✅ FCM sent to token {fcm_token[:10]}..., message ID: {response}")
        FCM_SENT.labels(status='success').inc()
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to send FCM to {fcm_token[:10]}...: {e}")
        FCM_SENT.labels(status='failure').inc()
        raise

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "fcm"})

@app.route('/send-notification', methods=['POST'])
def send_notification_endpoint():
    """Send FCM notification endpoint"""
    with FCM_PROCESSING_TIME.time():
        try:
            data = request.json
            
            # Extract data
            fcm_token = data.get('fcm_token')
            title = data.get('title', 'Notification')
            message = data.get('message', '')
            user_id = data.get('user_id')
            metadata = data.get('metadata', {})
            
            if not fcm_token:
                return jsonify({"error": "FCM token is required"}), 400
            
            if not message:
                return jsonify({"error": "Message content is required"}), 400
            
            # Prepare additional data
            notification_data = {
                "user_id": str(user_id) if user_id else "",
                "timestamp": str(metadata.get('timestamp', '')),
                "type": str(metadata.get('type', 'general'))
            }
            
            # Send FCM notification
            message_id = send_fcm_notification(fcm_token, title, message, notification_data)
            
            return jsonify({
                "status": "success",
                "message": "FCM notification sent successfully",
                "user_id": user_id,
                "message_id": message_id
            })
            
        except Exception as e:
            logger.error(f"Error in FCM endpoint: {e}")
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start Prometheus metrics server
    start_http_server(8003)
    logger.info("📊 FCM service metrics available at http://localhost:8003")
    
    logger.info("🚀 Starting FCM Microservice on port 5003")
    app.run(host="0.0.0.0", port=5003, debug=False)
