# Notifyy - Multi-Architecture Notification System

A comprehensive notification system supporting multiple deployment architectures: **Event-Driven Microservices** and **Kubernetes-based**. The system handles notifications across multiple channels including Email, WhatsApp, FCM Push Notifications, and Test endpoints.

## 🏗️ Architecture Overview

This project provides **two distinct architectural approaches** for different deployment scenarios:

### 1. Event-Driven Microservices Architecture (Current Directory)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Producer API  │───▶│   Kafka Topic   │───▶│  Event Router   │
│   (Port 5005)   │    │ notification-   │    │   (Port 8000)   │
└─────────────────┘    │    events       │    └─────────────────┘
                       └─────────────────┘             │
                                                       ▼
                    ┌─────────────────────────────────────────────────┐
                    │              Microservices Layer                │
                    ├─────────────┬─────────────┬─────────────┬───────┤
                    │    Email    │  WhatsApp   │     FCM     │ Test  │
                    │ (Port 5001) │(Port 5002)  │(Port 5003)  │(5004) │
                    │ Metrics:    │ Metrics:    │ Metrics:    │Metrics│
                    │    8001     │    8002     │    8003     │ 8004  │
                    └─────────────┴─────────────┴─────────────┴───────┘
```

### 2. Kubernetes-based Architecture (k8s_based Directory)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web App       │    │ Producer API    │    │   Monitoring    │
│ (Firebase PWA)  │    │ (REST Endpoints)│    │   (Grafana +    │
│                 │    │                 │    │  Prometheus)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │    Email    │ │  WhatsApp   │ │     FCM     │ │   Test    │ │
│  │   Service   │ │   Service   │ │   Service   │ │ Service   │ │
│  │             │ │             │ │             │ │           │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Architecture Comparison

| Feature | Event-Driven Microservices | Kubernetes-based |
|---------|----------------------------|------------------|
| **Deployment** | Docker Compose / Cloud Run | Kubernetes Cluster |
| **Event Processing** | Kafka + Event Router | Direct API Calls |
| **Scalability** | Horizontal (per service) | Kubernetes Auto-scaling |
| **Complexity** | Medium | Higher |
| **Monitoring** | Prometheus + Grafana | Grafana + Prometheus |
| **Service Discovery** | Environment Variables | Kubernetes DNS |
| **Best For** | Cloud-native, Event-driven | Enterprise, High-availability |

## 🔧 Technology Stack

### Common Components
- **Languages**: Python 3.9+
- **Web Framework**: Flask
- **Message Queue**: Apache Kafka
- **Database**: PostgreSQL
- **Monitoring**: Prometheus + Grafana
- **Containerization**: Docker

### Communication Channels
- **Email**: SMTP (Gmail) with App Passwords
- **WhatsApp**: Twilio API
- **Push Notifications**: Firebase Cloud Messaging (FCM)
- **Web App**: Progressive Web App with Firebase

## 🌟 Key Features

### Event-Driven Architecture Features
- ✅ **Asynchronous Processing**: Non-blocking event processing
- ✅ **Fault Tolerance**: Kafka ensures message durability
- ✅ **Scalability**: Independent service scaling
- ✅ **Observability**: Comprehensive metrics and logging
- ✅ **Flexibility**: Easy to add new notification channels

### Kubernetes Architecture Features
- ✅ **High Availability**: Pod replicas and auto-restart
- ✅ **Load Balancing**: Built-in service load balancing
- ✅ **Rolling Updates**: Zero-downtime deployments
- ✅ **Resource Management**: CPU/Memory limits and requests
- ✅ **Service Mesh**: Advanced networking capabilities

## 🚀 Deployment Options

### Option 1: Event-Driven Microservices (Recommended for Cloud)

#### Local Development
```bash
# Clone repository
git clone <repository-url>
cd kafka-project/event-driven

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start with Docker Compose
docker-compose up -d

# Check all services are running
docker-compose ps
```

#### Google Cloud Run Deployment
```bash
# Build and deploy each service
gcloud run deploy email-service --source ./email --port 5001
gcloud run deploy whatsapp-service --source ./whatsapp --port 5002
gcloud run deploy fcm-service --source ./fcm --port 5003
gcloud run deploy router-service --source . --port 8000

# Configure environment variables for each service
gcloud run services update email-service --set-env-vars="SENDER_EMAIL=your-email"
```

### Option 2: Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster (GKE, EKS, AKS, or local)
- kubectl configured
- Helm (optional)

#### Deploy to Kubernetes
```bash
cd kafka-project/k8s_based

# Apply Kubernetes manifests
kubectl apply -f k8s_files/

# Check deployment status
kubectl get pods
kubectl get services

# Access services
kubectl port-forward svc/producer-api 8080:80
```

## 📱 Web Application Features

The system includes a Progressive Web App (PWA) with:

### Features
- 📱 **Push Notification Registration**: Automatic FCM token generation
- 🔔 **Real-time Notifications**: Instant push notifications
- 📊 **Notification History**: View sent notifications
- 🎯 **Multi-channel Support**: Email, WhatsApp, Push
- 📈 **Analytics Dashboard**: Notification metrics

### Firebase Setup for Web App
1. Create Firebase project at [Firebase Console](https://console.firebase.google.com)
2. Enable Cloud Messaging
3. Generate Web Push certificates
4. Download service account key
5. Update `firebase-config.js` with your configuration

## 📈 Monitoring and Observability

### Metrics Available
- **Message Processing**: Throughput, latency, error rates
- **Service Health**: Uptime, response times, resource usage
- **Channel-specific**: Email delivery, WhatsApp status, FCM success rates
- **Business Metrics**: User engagement, notification types

### Grafana Dashboards
Pre-configured dashboards for:
- System Overview
- Service-specific metrics
- Error tracking
- Performance monitoring

### Alerting
Set up alerts for:
- Service downtime
- High error rates
- Message queue backlog
- Resource exhaustion

## 🧪 Testing and Development

### Load Testing
```bash
# Install testing tools
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:5005
```

### Integration Testing
```bash
# Run integration tests
python tests/integration_test.py

# Test individual services
curl http://localhost:5001/health  # Email service
curl http://localhost:5002/health  # WhatsApp service
curl http://localhost:5003/health  # FCM service
```

### Development Tips
1. **Use Test Service**: Send test notifications to `/test` endpoint
2. **Monitor Logs**: Use `docker-compose logs -f` for debugging
3. **Prometheus Metrics**: Check `/metrics` endpoints for service health
4. **Kafka UI**: Use tools like Kafdrop for Kafka monitoring

## 🔒 Security Considerations

### Credentials Management
- Use environment variables for all secrets
- Implement secret rotation for production
- Use cloud secret managers (Google Secret Manager, AWS Secrets Manager)

### Network Security
- Enable TLS for all communication
- Use VPC/private networks in cloud deployments
- Implement proper firewall rules

### API Security
- Add authentication/authorization
- Implement rate limiting
- Use API keys for service-to-service communication

### Data Privacy
- Encrypt sensitive data at rest
- Implement data retention policies
- Ensure GDPR compliance for user data

## 🔄 Migration Guide

### From Direct API to Event-Driven
1. Deploy event-driven services alongside existing APIs
2. Gradually migrate clients to use Producer API
3. Monitor both systems during transition
4. Decommission old APIs after full migration

### From Event-Driven to Kubernetes
1. Containerize all services (already done)
2. Create Kubernetes manifests
3. Set up persistent volumes for data
4. Configure ingress and load balancers
5. Migrate traffic gradually using blue-green deployment

## 🔧 Services (Event-Driven Architecture)

### 1. Event Router (`router.py`)

- Consumes events from Kafka topic `notification-events`
- Routes messages based on type to appropriate microservices
- Provides Prometheus metrics

### 2. Email Service (`email/app.py`)

- Sends emails via SMTP (Gmail)
- Endpoint: `POST /send-email`
- Port: 5001, Metrics: 8001

### 3. WhatsApp Service (`whatsapp/app.py`)

- Sends WhatsApp messages via Twilio
- Endpoint: `POST /send-whatsapp`
- Port: 5002, Metrics: 8002

### 4. FCM Service (`fcm/app.py`)

- Sends push notifications via Firebase Cloud Messaging
- Endpoint: `POST /send-notification`
- Port: 5003, Metrics: 8003

### 5. Test Service (`test/app.py`)

- Logs and stores test messages for debugging
- Endpoint: `POST /test`
- Port: 5004, Metrics: 8004

### 6. Producer Service (`producer.py`)

- API to send events to the notification system
- Various endpoints for different notification types
- Port: 5005, Metrics: 8005

## 📋 Message Types and Routing

### Order Notifications (`type: "order"`)

Routes to: Email + WhatsApp

### Promotion Notifications (`type: "promotion"`)

Routes to: Email + FCM Push

### Test Notifications (`type: "test"`)

Routes to: Test Service

## 📄 Message Format

```json
{
  "type": "order|promotion|test",
  "user_data": {
    "user_id": "123",
    "email": "user@example.com",
    "phone": "+1234567890",
    "fcm_token": "fcm_token_here",
    "name": "John Doe"
  },
  "content": {
    "title": "Notification Title",
    "message": "Notification message content"
  },
  "metadata": {
    "timestamp": "2025-01-01T00:00:00",
    "source": "api",
    "order_id": "ORD123"
  }
}
```

## ⚙️ Setup and Configuration

### 1. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Email Configuration
SENDER_EMAIL=your_email@gmail.com
APP_PASSWORD=your_gmail_app_password

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Firebase Configuration
FIREBASE_SERVICE_ACCOUNT_PATH=./credentials.json
```

### 2. Firebase Setup

1. Download your Firebase service account JSON file
2. Place it as `credentials.json` in the project root

### 3. Local Development

#### Start with Docker Compose:

```bash
docker-compose up -d
```

#### Or run services individually:

```bash
# Start Kafka and Zookeeper first
docker-compose up -d zookeeper kafka postgres

# Start services
python router.py
python email/app.py
python whatsapp/app.py
python fcm/app.py
python test/app.py
python producer.py
```

## 📚 API Examples

### Send Order Notification

```bash
curl -X POST http://localhost:5005/send-order-notification \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123",
    "email": "customer@example.com",
    "phone": "+1234567890",
    "name": "John Doe",
    "title": "Order Confirmed",
    "message": "Your order #12345 has been confirmed and will be delivered soon.",
    "order_id": "12345"
  }'
```

### Send Promotion

```bash
curl -X POST http://localhost:5005/send-promotion \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123",
    "email": "customer@example.com",
    "fcm_token": "fcm_token_here",
    "name": "John Doe",
    "title": "Special Offer",
    "message": "Get 50% off on your next order!",
    "campaign_id": "PROMO123"
  }'
```

### Send Test Message

```bash
curl -X POST http://localhost:5005/send-test \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "name": "Test User",
    "title": "Test Notification",
    "message": "This is a test message.",
    "test_id": "TEST123"
  }'
```

### Direct Service Calls

#### Email Service

```bash
curl -X POST http://localhost:5001/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "title": "Test Email",
    "message": "This is a test email.",
    "user_id": "123"
  }'
```

#### WhatsApp Service

```bash
curl -X POST http://localhost:5002/send-whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "title": "Test WhatsApp",
    "message": "This is a test WhatsApp message.",
    "user_id": "123"
  }'
```

#### FCM Service

```bash
curl -X POST http://localhost:5003/send-notification \
  -H "Content-Type: application/json" \
  -d '{
    "fcm_token": "your_fcm_token",
    "title": "Test Push",
    "message": "This is a test push notification.",
    "user_id": "123"
  }'
```

## 📊 Monitoring

### Prometheus Metrics

- Router: <http://localhost:8000/metrics>
- Email: <http://localhost:8001/metrics>
- WhatsApp: <http://localhost:8002/metrics>
- FCM: <http://localhost:8003/metrics>
- Test: <http://localhost:8004/metrics>
- Producer: <http://localhost:8005/metrics>

### Prometheus Dashboard

Access Prometheus at: <http://localhost:9090>

### Service Health Checks

All services expose `/health` endpoints:

- <http://localhost:5001/health> (Email)
- <http://localhost:5002/health> (WhatsApp)
- <http://localhost:5003/health> (FCM)
- <http://localhost:5004/health> (Test)

## ☁️ Production Deployment

### Environment-specific configurations

1. Update service URLs in environment variables
2. Use proper secrets management for credentials
3. Configure Kafka cluster endpoints
4. Set up proper monitoring and alerting
5. Use production-grade databases

### Cloud Run Deployment

Each service can be deployed as a separate Cloud Run service with appropriate environment variables and secrets.

## 🧪 Testing

### View Test Messages

```bash
curl http://localhost:5004/test/messages
```

### Clear Test Messages

```bash
curl -X POST http://localhost:5004/test/clear
```

### Service Statistics

```bash
curl http://localhost:5004/test/stats
```

## 🐛 Troubleshooting

1. **Kafka Connection Issues**: Ensure Kafka is running and accessible
2. **Email Failures**: Check Gmail app password and SMTP settings
3. **WhatsApp Issues**: Verify Twilio credentials and phone number format
4. **FCM Problems**: Ensure Firebase credentials file is accessible
5. **Service Discovery**: Check that all services are running on expected ports

## 📋 Logs

All services use structured logging. Check Docker logs:

```bash
docker-compose logs -f [service_name]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Apache Kafka for reliable event streaming
- Firebase for push notification infrastructure
- Twilio for WhatsApp messaging capabilities
- Prometheus for monitoring and observability
- All contributors and maintainers

---

**Built with ❤️ for scalable notification delivery**
