# Operations Manual - AI-Powered Development Assistant Bot

## 1. System Overview
[Brief recap of components from high_level_documentation.md]

## 2. Service Management
### 2.1 Starting Services
```bash
# Development
docker-compose up -d orchestrator architect implementer

# Production
kubectl apply -f k8s/deployments/
```

### 2.2 Stopping Services
```bash
# Graceful shutdown
kubectl scale deployment orchestrator --replicas=0
```

## 3. Monitoring
### 3.1 Key Metrics
- **Orchestrator**: Task queue length, error rate
- **Agents**: LLM API latency, token usage
- **Database**: Connection pool usage, query latency

### 3.2 Alert Thresholds
- CPU >80% for 5 minutes
- Error rate >5% in 15-minute window

## 4. Backup Procedures
### 4.1 PostgreSQL
```bash
pg_dump -Fc -U botadmin -d botdb > botdb.dump
```

### 4.2 Vector Database
```bash
# Snapshot index
curl -X POST http://vector-db:8080/snapshot
```

## 5. Troubleshooting
### 5.1 Bot Unresponsive
**Symptoms**: No response to commands  
**Check**: 
1. Orchestrator health endpoint
2. Telegram API status
3. Credit balance

### 5.2 Credit Deduction Errors
**Symptoms**: Transactions failing  
**Check**:
1. Database connection
2. Sufficient credits
3. Fraud detection locks

## 6. Escalation
- **Technical Issues**: DevOps Team
- **Billing Issues**: Finance Team
- **Security Incidents**: CISO Office