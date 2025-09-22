import logging
import time
import os
from confluent_kafka import Consumer, TopicPartition
from prometheus_client import start_http_server, Counter, Gauge, Histogram

logging.basicConfig(level=logging.INFO)
server = os.getenv("SERVER", 'localhost:9092')
# Prometheus metrics
messages_consumed = Counter('kafka_messages_consumed', 'Number of messages consumed from Kafka')
consumer_lag = Gauge('kafka_consumer_lag', 'Consumer lag for Kafka partition')
message_size_histogram = Histogram('kafka_message_size_bytes', 'Message size in bytes')
processing_time_histogram = Histogram('kafka_processing_time_seconds', 'Time to process each batch of messages')

def main():
    start_http_server(8000)

    consumer_config = {
        'bootstrap.servers': server,  
        'group.id': 'test',
        'auto.offset.reset': 'earliest'
    }

    topic_name = 'notification-topic'     
    partition_number = 1      

    consumer = Consumer(consumer_config)
    tp = TopicPartition(topic_name, partition_number)
    consumer.assign([tp])

    logging.info("Starting to consume messages...")

    while True:
        start_time = time.time()

        
        low, high = consumer.get_watermark_offsets(tp, timeout=1, cached=False)

       
        msgs = consumer.consume(num_messages=10, timeout=1.0)
        for msg in msgs:
            if msg is None or msg.error():
                continue
            messages_consumed.inc()
            message_size_histogram.observe(len(msg.value()) if msg.value() else 0)
            logging.info(
                f"Partition={msg.partition()}, Offset={msg.offset()}, "
                f"Key={msg.key()}, Value={msg.value()}"
            )

        
        end_time = time.time()
        processing_time_histogram.observe(end_time - start_time)

        
        current_position = consumer.position([tp])[0].offset
        lag = high - current_position if current_position >= 0 else 0
        consumer_lag.set(lag)

        
        time.sleep(1)

if __name__ == '__main__':
    main()