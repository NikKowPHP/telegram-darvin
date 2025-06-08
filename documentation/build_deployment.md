# Build and Deployment Guide - AI-Powered Development Assistant Bot

## 1. Prerequisites
[Existing content remains unchanged]

## 2. Configuration
### 2.1 Service-Specific Environment Variables
```bash
# Orchestrator
export ORCHESTRATOR_PORT=8000
export TASK_TIMEOUT=300

# Implementer Agent
export MAX_CODE_LENGTH=2000
export LLM_TEMPERATURE=0.7

# Billing Service
export CREDIT_RATE=0.5
export CURRENCY=USD
```

### 2.2 Kubernetes Secrets
```bash
kubectl create secret generic bot-secrets \
  --from-literal=telegram-token=$TELEGRAM_TOKEN \
  --from-literal=openai-key=$OPENAI_KEY \
  --from-literal=postgres-url=$POSTGRES_URL
```

## 3. Kubernetes Deployment
### 3.1 Orchestrator Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orchestrator
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: orchestrator
        image: orchestrator:1.0.0
        envFrom:
        - secretRef:
            name: bot-secrets
```

### 3.2 Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: orchestrator-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: orchestrator
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
```

## 4. Rollback Procedures
```bash
# Rollback to previous deployment
kubectl rollout undo deployment/orchestrator

# Verify status
kubectl get pods -l app=orchestrator