

#!/usr/bin/env python3
"""
Email Microservice
Handles email notifications via SMTP
"""

from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage
import os
import logging
from prometheus_client import Counter, Histogram, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
EMAILS_SENT = Counter('email_sent_total', 'Total emails sent', ['status'])
EMAIL_PROCESSING_TIME = Histogram('email_processing_seconds', 'Time spent processing emails')

# Email credentials from environment variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "cybernet127001@gmail.com")
APP_PASSWORD = os.getenv("APP_PASSWORD", "app_pass")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))

def send_email(to_email, subject, content):
    """Send email via SMTP"""
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg.set_content(content)
        
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        
        logger.info(f"✅ Email sent to {to_email} with subject '{subject}'")
        EMAILS_SENT.labels(status='success').inc()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {e}")
        EMAILS_SENT.labels(status='failure').inc()
        raise

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "email"})

@app.route('/send-email', methods=['POST'])
def send_email_endpoint():
    """Send email endpoint for microservice architecture"""
    with EMAIL_PROCESSING_TIME.time():
        try:
            data = request.json
            
            # Extract data
            to_email = data.get('email')
            subject = data.get('title', 'Notification')
            content = data.get('message', '')
            user_id = data.get('user_id')
            
            if not to_email:
                return jsonify({"error": "Email address is required"}), 400
            
            if not content:
                return jsonify({"error": "Message content is required"}), 400
            
            # Send email
            send_email(to_email, subject, content)
            
            return jsonify({
                "status": "success",
                "message": "Email sent successfully",
                "user_id": user_id,
                "email": to_email
            })
            
        except Exception as e:
            logger.error(f"Error in email endpoint: {e}")
            return jsonify({"error": str(e)}), 500

# Legacy endpoint for backward compatibility
@app.route('/register', methods=['POST'])
def register():
    """Legacy endpoint"""
    try:
        data = request.json
        send_email(data['email'], data.get("type", "Notification"), data.get("content", ""))
        return jsonify({"status": "Email Sent"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start Prometheus metrics server
    start_http_server(8001)
    logger.info("📊 Email service metrics available at http://localhost:8001")
    
    logger.info("🚀 Starting Email Microservice on port 5001")
    app.run(host="0.0.0.0", port=5001, debug=False)
