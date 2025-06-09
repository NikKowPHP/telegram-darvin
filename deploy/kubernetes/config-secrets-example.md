# Kubernetes ConfigMap and Secret Structure Examples

## app-config (ConfigMap)
This ConfigMap would hold non-sensitive configuration.
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_ENV: "production"
  LOG_LEVEL: "INFO"
  POSTGRES_SERVER: "postgres"
  POSTGRES_PORT: "5432"
  POSTGRES_DB: "ai_dev_bot"
  REDIS_HOST: "redis"
  REDIS_PORT: "6379"
  REDIS_DB: "0"
  PLATFORM_CREDIT_VALUE_USD: "0.01"
  MARKUP_FACTOR: "1.5"
```

## app-secrets (Secret)
This Secret would hold sensitive data. Values should be base64 encoded when applied.
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  TELEGRAM_BOT_TOKEN: "BASE64_ENCODED_TELEGRAM_TOKEN"
  GOOGLE_API_KEY: "BASE64_ENCODED_GOOGLE_API_KEY"
  OPENROUTER_API_KEY: "BASE64_ENCODED_OPENROUTER_API_KEY"
  API_KEY_ENCRYPTION_KEY: "BASE64_ENCODED_ENCRYPTION_KEY"
```

## postgres-secret (Secret)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
data:
  user: "BASE64_ENCODED_POSTGRES_USER"
  password: "BASE64_ENCODED_POSTGRES_PASSWORD"