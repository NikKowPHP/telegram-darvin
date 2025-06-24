import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.api_key_models import APIKey
from app.core.config import settings
from cryptography.fernet import Fernet
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)


class APIKeyManager:
    def __init__(self):
        # Load encryption key from settings
        self.encryption_key = settings.API_KEY_ENCRYPTION_KEY
        self.cipher = Fernet(self.encryption_key)

        # Initialize in-memory cache
        self.api_keys: Dict[str, List[str]] = {}
        self.current_indices: Dict[str, int] = {}
        self.load_keys_from_db()

    def load_keys_from_db(self):
        """Load active API keys from the database."""
        db: Session = next(get_db())
        try:
            active_keys = db.query(APIKey).filter(APIKey.is_active == True).all()
            for key in active_keys:
                if key.provider not in self.api_keys:
                    self.api_keys[key.provider] = []
                    self.current_indices[key.provider] = 0

                # Decrypt the key
                decrypted_key = self.cipher.decrypt(key.encrypted_key.encode()).decode()
                self.api_keys[key.provider].append(decrypted_key)

                # Update usage stats
                key.usage_count += 1
                key.last_used = func.now()
                db.commit()

            logger.info(f"Loaded {len(active_keys)} active API keys from database.")
            if not self.api_keys:
                logger.warning("No active API keys found in the database!")
        except Exception as e:
            logger.error(f"Error loading API keys from database: {str(e)}")
            # Fallback to settings if DB access fails
            self.api_keys = {
                "google": [settings.GOOGLE_API_KEY] if settings.GOOGLE_API_KEY else [],
                "openrouter": (
                    [settings.OPENROUTER_API_KEY] if settings.OPENROUTER_API_KEY else []
                ),
            }
            for provider in self.api_keys:
                self.current_indices[provider] = 0
            logger.warning("Fallback to settings-based API keys.")

    def get_next_key(self, provider: str) -> Optional[str]:
        try:
            if provider not in self.api_keys or not self.api_keys[provider]:
                logger.error(
                    f"No API keys configured for provider: {provider}",
                    extra={
                        "provider": provider,
                        "available_providers": list(self.api_keys.keys()),
                    },
                )
                return None

            keys = self.api_keys[provider]
            current_index = self.current_indices[provider]
            key = keys[current_index]
            self.current_indices[provider] = (current_index + 1) % len(keys)
            return key
        except Exception as e:
            logger.error(
                f"Unexpected error getting API key for provider {provider}: {str(e)}",
                exc_info=True,
                extra={"provider": provider},
            )
            return None
