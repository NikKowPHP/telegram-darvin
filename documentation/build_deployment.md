# Build and Deployment Guide - AI-Powered Development Assistant Bot

## 1. Prerequisites
- Docker 20.10+
- Kubernetes cluster (minikube for development)
- Telegram Bot API token
- OpenAI API key (or other LLM provider)

## 2. Configuration
### 2.1 Environment Variables
```bash
# Required for all services
export TELEGRAM_TOKEN="your_bot_token"
export OPENAI_KEY="your_llm_key"

# Database configuration
export PGUSER=botadmin
export PGPASSWORD=securepassword
```

### 2.2 Secrets Management
```bash
# Create Kubernetes secret
kubectl create secret generic bot-secrets \
  --from-literal=telegram-token=$TELEGRAM_TOKEN \
  --from-literal=openai-key=$OPENAI_KEY
```

## 3. Building Containers
```bash
# Build all services
docker-compose build orchestrator architect implementer

# Build specific service
docker-compose build orchestrator
```

## 4. Deployment
### 4.1 Development
```bash
docker-compose up -d
```

### 4.2 Production (Kubernetes)
```bash
# Apply deployments
kubectl apply -f k8s/orchestrator.yaml
kubectl apply -f k8s/architect.yaml
kubectl apply -f k8s/implementer.yaml

# Verify status
kubectl get pods -w