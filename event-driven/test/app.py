#!/usr/bin/env python3
"""
Test Microservice
Handles test notifications for development and debugging
"""

from flask import Flask, request, jsonify
import os
import logging
import json
from datetime import datetime
from prometheus_client import Counter, Histogram, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
TEST_REQUESTS = Counter('test_requests_total', 'Total test requests received')
TEST_PROCESSING_TIME = Histogram('test_processing_seconds', 'Time spent processing test requests')

# Store test messages in memory (for demo purposes)
test_messages = []

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "test"})

@app.route('/test', methods=['POST'])
def test_endpoint():
    """Test endpoint that logs and stores test messages"""
    with TEST_PROCESSING_TIME.time():
        try:
            TEST_REQUESTS.inc()
            
            data = request.json
            timestamp = datetime.now().isoformat()
            
            # Create test message record
            test_message = {
                "timestamp": timestamp,
                "user_id": data.get('user_id'),
                "title": data.get('title', 'Test Notification'),
                "message": data.get('message', ''),
                "metadata": data.get('metadata', {}),
                "full_payload": data
            }
            
            # Store in memory
            test_messages.append(test_message)
            
            # Keep only last 100 messages
            if len(test_messages) > 100:
                test_messages.pop(0)
            
            logger.info(f"📝 Test message received: {json.dumps(test_message, indent=2)}")
            
            return jsonify({
                "status": "success",
                "message": "Test message received and logged",
                "timestamp": timestamp,
                "user_id": data.get('user_id'),
                "total_messages": len(test_messages)
            })
            
        except Exception as e:
            logger.error(f"Error in test endpoint: {e}")
            return jsonify({"error": str(e)}), 500

@app.route('/test/messages', methods=['GET'])
def get_test_messages():
    """Get all stored test messages"""
    return jsonify({
        "total_messages": len(test_messages),
        "messages": test_messages
    })

@app.route('/test/clear', methods=['POST'])
def clear_test_messages():
    """Clear all test messages"""
    global test_messages
    count = len(test_messages)
    test_messages = []
    return jsonify({
        "status": "success",
        "message": f"Cleared {count} test messages"
    })

@app.route('/test/stats', methods=['GET'])
def test_stats():
    """Get test service statistics"""
    return jsonify({
        "service": "test",
        "total_messages": len(test_messages),
        "latest_message": test_messages[-1] if test_messages else None,
        "uptime": "running"
    })

if __name__ == '__main__':
    # Start Prometheus metrics server
    start_http_server(8004)
    logger.info("📊 Test service metrics available at http://localhost:8004")
    
    logger.info("🚀 Starting Test Microservice on port 5004")
    app.run(host="0.0.0.0", port=5004, debug=False)
