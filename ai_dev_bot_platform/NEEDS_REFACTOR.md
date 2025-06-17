Missing environment variables detected in test runs. Please ensure the following environment variables are properly set in either `.env` or `.env.production`:

Required Variables:
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_SERVER
- POSTGRES_PORT
- POSTGRES_DB
- TELEGRAM_BOT_TOKEN
- API_KEY_ENCRYPTION_KEY

Steps to resolve:
1. Create/update `.env` file in project root with the required variables
2. Verify database connection settings match your PostgreSQL configuration
3. Ensure the encryption key is a secure random string
4. Run tests again with `pytest --disable-warnings`