import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

REQUIRED_ENV_VARS = [
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_SERVER",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "TELEGRAM_BOT_TOKEN",
    "API_KEY_ENCRYPTION_KEY",
]

PLACEHOLDER_VALUES = [
    "your_postgres_user",
    "your_postgres_password",
    "your_postgres_host",
    "your_postgres_port",
    "your_postgres_db_name",
    "your_telegram_bot_token_here",
    "your_secure_encryption_key_here",
]


def test_required_env_vars_set():
    for var in REQUIRED_ENV_VARS:
        assert (
            os.getenv(var) is not None
        ), f"Missing required environment variable: {var}"


def test_env_vars_not_using_placeholders():
    for var, placeholder in zip(REQUIRED_ENV_VARS, PLACEHOLDER_VALUES):
        value = os.getenv(var)
        assert (
            value != placeholder
        ), f"Environment variable {var} is using placeholder value"
