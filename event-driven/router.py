#!/usr/bin/env python3
"""
Event Router Service
Consumes messages from Kafka and routes them to appropriate microservices
"""

import json
import os
import asyncio
import aiohttp
import logging
from confluent_kafka import Consumer
from prometheus_client import start_http_server, Counter, Histogram

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
MESSAGES_PROCESSED = Counter('router_messages_processed_total', 'Total messages processed', ['message_type'])
MESSAGES_ROUTED = Counter('router_messages_routed_total', 'Messages routed to services', ['service', 'status'])
ROUTING_TIME = Histogram('router_processing_seconds', 'Time spent routing messages')

# Service URLs from environment
SERVICES = {
    'email': os.getenv('EMAIL_SERVICE_URL', 'http://localhost:5001/send-email'),
    'whatsapp': os.getenv('WHATSAPP_SERVICE_URL', 'http://localhost:5002/send-whatsapp'),
    'fcm': os.getenv('FCM_SERVICE_URL', 'http://localhost:5003/send-notification'),
    'test': os.getenv('TEST_SERVICE_URL', 'http://localhost:5004/test')
}

# Kafka configuration
KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('KAFKA_SERVERS', 'localhost:9092'),
    'group.id': os.getenv('KAFKA_GROUP', 'notification_router'),
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 1000
}

class EventRouter:
    def __init__(self):
        self.consumer = Consumer(KAFKA_CONFIG)
        self.session = None
        
    async def send_to_service(self, service_url, payload):
        """Send request to microservice"""
        try:
            async with self.session.post(service_url, json=payload, timeout=10) as response:
                if response.status == 200:
                    result = await response.json()
                    return {'status': 'success', 'response': result}
                else:
                    return {'status': 'error', 'error': f'HTTP {response.status}'}
        except Exception as e:
            logger.error(f"Error sending to {service_url}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def route_message(self, message_data):
        """Route message based on type"""
        with ROUTING_TIME.time():
            message_type = message_data.get('type')
            user_data = message_data.get('user_data', {})
            content = message_data.get('content', {})
            
            MESSAGES_PROCESSED.labels(message_type=message_type).inc()
            
            # Prepare payload for services
            payload = {
                'user_id': user_data.get('user_id'),
                'email': user_data.get('email'),
                'phone': user_data.get('phone'),
                'fcm_token': user_data.get('fcm_token'),
                'title': content.get('title', 'Notification'),
                'message': content.get('message', ''),
                'metadata': message_data.get('metadata', {})
            }
            
            results = []
            
            if message_type == 'order':
                # Send to email and whatsapp
                email_result = await self.send_to_service(SERVICES['email'], payload)
                whatsapp_result = await self.send_to_service(SERVICES['whatsapp'], payload)
                
                MESSAGES_ROUTED.labels(service='email', status=email_result['status']).inc()
                MESSAGES_ROUTED.labels(service='whatsapp', status=whatsapp_result['status']).inc()
                
                results.extend([email_result, whatsapp_result])
                
            elif message_type == 'promotion':
                # Send to email and FCM
                email_result = await self.send_to_service(SERVICES['email'], payload)
                fcm_result = await self.send_to_service(SERVICES['fcm'], payload)
                
                MESSAGES_ROUTED.labels(service='email', status=email_result['status']).inc()
                MESSAGES_ROUTED.labels(service='fcm', status=fcm_result['status']).inc()
                
                results.extend([email_result, fcm_result])
                
            elif message_type == 'test':
                # Send to test service
                test_result = await self.send_to_service(SERVICES['test'], payload)
                MESSAGES_ROUTED.labels(service='test', status=test_result['status']).inc()
                results.append(test_result)
                
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
            return results
    
    async def consume_messages(self):
        """Main consumer loop"""
        self.consumer.subscribe(['notification-events'])
        self.session = aiohttp.ClientSession()
        
        logger.info("🚀 Event router started, listening for messages...")
        
        try:
            while True:
                msg = self.consumer.poll(1.0)
                
                if msg is None:
                    await asyncio.sleep(0.1)
                    continue
                    
                if msg.error():
                    logger.error(f"Kafka error: {msg.error()}")
                    continue
                
                try:
                    # Parse message
                    message_data = json.loads(msg.value().decode('utf-8'))
                    logger.info(f"📨 Received message: {message_data}")
                    
                    # Route message
                    results = await self.route_message(message_data)
                    logger.info(f"✅ Routing results: {results}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            if self.session:
                await self.session.close()
            self.consumer.close()

async def main():
    # Start Prometheus metrics server
    start_http_server(8000)
    logger.info("📊 Prometheus metrics available at http://localhost:8000")
    
    # Start event router
    router = EventRouter()
    await router.consume_messages()

if __name__ == '__main__':
    asyncio.run(main())
