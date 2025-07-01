# 📣 Kafka-Based Notification System

A scalable, event-driven microservice system using **Apache Kafka**, built to send **email**, **WhatsApp**, and **push notifications**. Consumers and producers are deployed in **Kubernetes**, monitored via **Prometheus** and **Grafana**, while push notifications are received on a **local website** for testing.

---

## 🏗️ System Architecture

```
[Producer API] (K8s Pod)
     ↓
[Kafka Broker] (GCP VM)
     ↓
├── email-topic (2 partitions) ─▶ Email Consumer (K8s)
├── notification-topic (2 partitions)
│   ├─▶ WhatsApp & FCM Consumer (K8s)
│   ├─▶ Push Notification logic (K8s)
│   └─▶ Benchmark/Log Consumer (K8s)
     
[Website] (localhost) ◀─── Push notification from FCM
     
[Prometheus + Grafana] (GCP VM) ◀─── Metrics from consumers
```

---

## ⚙️ Tech Stack

* **Kafka** – Deployed on GCP VM
* **Kubernetes** – All consumers and producer API deployed here
* **Flask** – Producer API
* **Confluent Kafka (Python client)**
* **FCM** – Push notifications (tested on local site via HTTP)
* **Email/WhatsApp APIs** – External service integrations
* **Prometheus + Grafana** – Metrics and dashboard, deployed in GCP VM

---

## 🔧 Setup Guide

### 📦 Kafka Setup (on GCP VM)

Ensure Kafka is running and has the following topics:

```bash
# Create topics if not already created
bin/kafka-topics.sh --create --topic email-topic --bootstrap-server localhost:9092 --partitions 2 --replication-factor 1
bin/kafka-topics.sh --create --topic notification-topic --bootstrap-server localhost:9092 --partitions 2 --replication-factor 1
```

### 🚀 Deploy to Kubernetes

All services are containerized and deployed to Kubernetes using standard `Deployment` and `Service` manifests.

```bash
kubectl apply -f k8s/email-consumer.yaml
kubectl apply -f k8s/whatsapp-consumer.yaml
kubectl apply -f k8s/push-consumer.yaml
kubectl apply -f k8s/benchmark-consumer.yaml
kubectl apply -f k8s/producer-api.yaml
```

> Ensure all pods can reach the Kafka broker (use internal IP or VPC IP of VM).

---

## 📤 Producer API (Flask)

### Run inside cluster (or local port-forward)

Send Kafka messages:

```bash
curl -X POST "http://<producer-service>:5000/send-kafka" \
  -H "Content-Type: application/json" \
  -d '{
    "no": 1,
    "type": "order",
    "content": "Your order is confirmed!",
    "topic": "notification-topic",
    "partition": 1
  }'
```

---

## 📬 Consumers Behavior

* **Email Consumer**:

  * Reads from `email-topic` (both partitions)
  * Filters messages by type (`promotion`, `order`)
  * Sends emails accordingly

* **WhatsApp + Push Notification Consumer**:

  * Reads from `notification-topic`
  * Sends WhatsApp and FCM-based push notifications

* **Benchmark Consumer**:

  * Only listens to `notification-topic` → Partition 2
  * Tracks throughput, errors, logs system health
  * Sends custom metrics to Prometheus

---

## 📊 Monitoring: Prometheus + Grafana (on VM)

**Prometheus** scrapes `/metrics` from each consumer API via NodePort or ClusterIP + VPC routing.

**Grafana Dashboard Includes:**

* Total messages received
* Messages by type: Email / WhatsApp / Push
* Failed messages
* Partition-wise message count
* Latency (if benchmarked)
* Per-service counters

---

## 🔔 Push Notifications (Localhost Website)

* Website runs on **localhost** due to `http://` restrictions.
* FCM requires HTTPS for production; testing is done via local service worker.
* The push consumer sends notifications to FCM, and the browser receives it using registered token.

---

## 📁 Folder Structure

```
.
├── k8s/                    # Kubernetes manifests
│   ├── email-consumer.yaml
│   ├── whatsapp-consumer.yaml
│   ├── push-consumer.yaml
│   ├── benchmark-consumer.yaml
│   └── producer-api.yaml
├── consumers/
│   └── *.py                # Consumer logic
├── producer_api.py         # Kafka producer API (Flask)
├── dashboard/
│   └── grafana_dashboard.json
├── metrics/
│   └── prometheus_metrics.py
├── website/                # Push notification demo
│   └── index.html, sw.js
├── requirements.txt
└── README.md
```

---

## 📌 Notes

* Kafka exposed only within VPC for security.
* Consumers send metrics via `prometheus_client`:

```python
from prometheus_client import Counter

EMAILS_SENT = Counter("emails_sent_total", "Number of emails sent")
```

* Localhost push notification is for development only.

---

## 🔮 Future Enhancements

* Expose website securely with HTTPS + SSL termination
* Add Dead Letter Queue (DLQ) support for failed messages
* Retry logic and idempotent message handling
* Auto-scaling consumers using HPA
* Add Jaeger/OpenTelemetry for tracing

---

## 🤝 Contributions

Pull requests and issues are welcome! Please fork and open a PR.

---

## 📝 License

MIT License © 2025 \[Your Name]
