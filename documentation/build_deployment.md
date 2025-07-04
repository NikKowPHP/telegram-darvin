# Build and Deployment Guide - AI-Powered Development Assistant Bot

## 1. Prerequisites
[Existing content remains unchanged]

## 2. Configuration
### 2.1 Service-Specific Environment Variables
```bash
# Required for all services that interact with LLMs
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google_cloud_service_account.json" # For direct Gemini
# OR individual Google API keys if not using ADC for all Google services
# export GOOGLE_API_KEY_1="your_gemini_key_1"
export OPENROUTER_API_KEY_1="your_openrouter_key_1"
export OPENROUTER_API_KEY_2="your_openrouter_key_2" # Example for multiple keys

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
# Create Kubernetes secret for Google Cloud (if using service account file)
kubectl create secret generic google-cloud-sa --from-file=credentials.json=/path/to/your/google_cloud_service_account.json

# Create Kubernetes secret for API Keys
kubectl create secret generic llm-api-keys \
  --from-literal=openrouter-key-1=$OPENROUTER_API_KEY_1 \
  --from-literal=openrouter-key-2=$OPENROUTER_API_KEY_2
  # Add direct Google API keys here if not using ADC or if they are separate
  # --from-literal=google-api-key-1=$GOOGLE_API_KEY_1
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