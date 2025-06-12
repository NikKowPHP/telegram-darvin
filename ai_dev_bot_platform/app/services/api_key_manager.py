import logging
from typing import Dict, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class APIKeyManager:
    def __init__(self):
        # For simplicity, load directly from settings for now.
        # Later, this can load from DB, handle encryption, round-robin from pools etc.
        self.api_keys: Dict[str, List[str]] = {
            "google": [settings.GOOGLE_API_KEY] if settings.GOOGLE_API_KEY else [],
            "openrouter": [settings.OPENROUTER_API_KEY] if settings.OPENROUTER_API_KEY else [],
        }
        self.current_indices: Dict[str, int] = {
            provider: 0 for provider in self.api_keys
        }
        logger.info("APIKeyManager initialized with keys from settings.")
        if not self.api_keys["google"] and not self.api_keys["openrouter"]:
            logger.warning("No API keys configured for Google Gemini or OpenRouter!")

    def get_next_key(self, provider: str) -> Optional[str]:
        try:
            if provider not in self.api_keys or not self.api_keys[provider]:
                logger.error(
                    f"No API keys configured for provider: {provider}",
                    extra={"provider": provider, "available_providers": list(self.api_keys.keys())}
                )
                return None

            keys = self.api_keys[provider]
            current_index = self.current_indices[provider]
            key = keys[current_index]
            self.current_indices[provider] = (current_index + 1) % len(keys)
            return key
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error accessing API key for provider {provider}: {str(e)}",
                exc_info=True,
                extra={
                    "provider": provider,
                    "status_code": e.response.status_code,
                    "request_url": e.request.url
                }
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error getting API key for provider {provider}: {str(e)}",
                exc_info=True,
                extra={"provider": provider}
            )
            return None

# Singleton instance or inject as dependency
# api_key_manager_instance = APIKeyManager()