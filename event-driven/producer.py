#!/usr/bin/env python3
"""
Event Producer Service
Produces notification events to Kafka topic
"""

from flask import Flask, request, jsonify
import json
import os
import logging
from datetime import datetime
from confluent_kafka import Producer
from prometheus_client import Counter, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
EVENTS_PRODUCED = Counter('events_produced_total', 'Total events produced', ['event_type'])

# Kafka configuration
KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('KAFKA_SERVERS', 'localhost:9092'),
    'client.id': 'notification_producer'
}

TOPIC_NAME = os.getenv('KAFKA_TOPIC', 'notification-events')

# Initialize Kafka producer
producer = Producer(KAFKA_CONFIG)

def delivery_report(err, msg):
    """Callback for message delivery reports"""
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "producer"})

@app.route('/send-notification', methods=['POST'])
def send_notification():
    """Send notification event to Kafka"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('type'):
            return jsonify({"error": "Event type is required"}), 400
        
        if not data.get('user_data'):
            return jsonify({"error": "User data is required"}), 400
        
        # Create event message
        event = {
            "type": data.get('type'),  # order, promotion, test
            "user_data": data.get('user_data'),  # user information
            "content": data.get('content', {}),  # notification content
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "source": "api",
                "request_id": data.get('request_id', ''),
                **data.get('metadata', {})
            }
        }
        
        # Send to Kafka
        producer.produce(
            TOPIC_NAME,
            value=json.dumps(event),
            callback=delivery_report
        )
        producer.flush()
        
        EVENTS_PRODUCED.labels(event_type=event['type']).inc()
        
        logger.info(f"📤 Event sent to Kafka: {event['type']}")
        
        return jsonify({
            "status": "success",
            "message": "Event sent to notification system",
            "event_type": event['type'],
            "user_id": event['user_data'].get('user_id')
        })
        
    except Exception as e:
        logger.error(f"Error sending event: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/send-order-notification', methods=['POST'])
def send_order_notification():
    """Convenience endpoint for order notifications"""
    try:
        data = request.json
        
        event = {
            "type": "order",
            "user_data": {
                "user_id": data.get('user_id'),
                "email": data.get('email'),
                "phone": data.get('phone'),
                "name": data.get('name', '')
            },
            "content": {
                "title": data.get('title', 'Order Confirmation'),
                "message": data.get('message', 'Your order has been confirmed.')
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "source": "order_api",
                "order_id": data.get('order_id', '')
            }
        }
        
        # Forward to main endpoint
        return send_notification_internal(event)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send-promotion', methods=['POST'])
def send_promotion():
    """Convenience endpoint for promotion notifications"""
    try:
        data = request.json
        
        event = {
            "type": "promotion",
            "user_data": {
                "user_id": data.get('user_id'),
                "email": data.get('email'),
                "fcm_token": data.get('fcm_token'),
                "name": data.get('name', '')
            },
            "content": {
                "title": data.get('title', 'Special Offer'),
                "message": data.get('message', 'Check out our latest promotion!')
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "source": "marketing_api",
                "campaign_id": data.get('campaign_id', '')
            }
        }
        
        return send_notification_internal(event)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send-test', methods=['POST'])
def send_test():
    """Convenience endpoint for test notifications"""
    try:
        data = request.json
        
        event = {
            "type": "test",
            "user_data": {
                "user_id": data.get('user_id', 'test_user'),
                "name": data.get('name', 'Test User')
            },
            "content": {
                "title": data.get('title', 'Test Notification'),
                "message": data.get('message', 'This is a test message.')
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "source": "test_api",
                "test_id": data.get('test_id', '')
            }
        }
        
        return send_notification_internal(event)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_notification_internal(event):
    """Internal function to send event to Kafka"""
    try:
        producer.produce(
            TOPIC_NAME,
            value=json.dumps(event),
            callback=delivery_report
        )
        producer.flush()
        
        EVENTS_PRODUCED.labels(event_type=event['type']).inc()
        
        return jsonify({
            "status": "success",
            "message": f"{event['type'].title()} notification sent",
            "event_type": event['type'],
            "user_id": event['user_data'].get('user_id')
        })
        
    except Exception as e:
        logger.error(f"Error sending event: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start Prometheus metrics server
    start_http_server(8005)
    logger.info("📊 Producer service metrics available at http://localhost:8005")
    
    logger.info("🚀 Starting Event Producer Service on port 5005")
    app.run(host="0.0.0.0", port=5005, debug=False)
