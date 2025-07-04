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
- **Agents**: LLM API latency and error rates specifically for Google Gemini calls and OpenRouter calls. Token usage breakdown by provider.
- **Database**: Connection pool usage, query latency

### 3.2 Alert Thresholds
- CPU >80% for 5 minutes
- Error rate >5% in 15-minute window

## 4. Utility Scripts

### 4.1 CLI Runner
The `cli_runner.py` script provides command-line access to core application functionality.

**Usage**:
```bash
python cli_runner.py [command] [options]
```

**Common Commands**:
- `run-task [task_id]`: Execute a specific development task
- `verify-project [project_id]`: Run verification checks on a project
- `--help`: Show available commands

### 4.2 Database Seeder
The `seed_db.py` script populates the database with initial test data.

**Usage**:
```bash
python seed_db.py [options]
```

**Options**:
- `--reset`: Clear existing data before seeding
- `--sample-size=N`: Number of test records to create
- `--env=ENV`: Target environment (dev/test/prod)

## 5. Backup Procedures
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
### 5.X New Troubleshooting Item: Provider-Specific API Issues
**Symptoms**: Errors related to "Google API" or "OpenRouter API," specific HTTP error codes (e.g., 429 from a specific provider, authentication errors).
**Check**:
1. Validity and permissions of Google Cloud credentials or relevant OpenRouter API keys.
2. Quotas on the Google Cloud project or OpenRouter account.
3. Status pages for Google Cloud AI services and OpenRouter.
4. Network connectivity to `*.googleapis.com` and `openrouter.ai`.

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