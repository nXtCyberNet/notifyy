from confluent_kafka import Producer
import random 

# Kafka configuration
conf = {
    'bootstrap.servers': 'localhost:9092'  # Update if needed
}

# Create producer instance
producer = Producer(conf)
mess = ["order","delivered", "shipped", "cancelled", "pending"]

# Message format: order_id,type,content
test_message = f"1,order,delivered  {mess[random.randint(0, 4)]}"

# Delivery report callback
def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Message delivered to {msg.topic()} [{msg.partition()}]")

# Send the message to topic 'app-topic'
i =  0 
'''
while i < 100:
    test_message = f"{i},notification,Your order has been shipped"
    
    producer.produce('notification-topic', test_message.encode('utf-8'), callback=delivery_report)
    i += 1
    '''
producer.produce('notification-topic', test_message.encode('utf-8'), callback=delivery_report)
# Wait for delivery
producer.flush()
