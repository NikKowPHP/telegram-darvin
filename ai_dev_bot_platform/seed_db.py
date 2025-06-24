import os
import sys
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet

# Add the app directory to the path to make imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.db.session import SessionLocal, engine
from app.models.api_key_models import APIKey, Base
from app.core.config import settings

# Load environment variables from .env file
load_dotenv()

def seed_api_keys():
    """
    Reads API keys from the .env file and inserts them into the database if they don't already exist.
    """
    db: Session = SessionLocal()
    
    # Ensure the table exists
    Base.metadata.create_all(bind=engine)

    # Prepare the cipher for encryption
    try:
        cipher = Fernet(settings.API_KEY_ENCRYPTION_KEY.encode())
    except Exception as e:
        print(f"Error: Invalid API_KEY_ENCRYPTION_KEY. It must be 32 url-safe base64-encoded bytes. Error: {e}")
        return

    # List of keys to seed from settings
    keys_to_seed = {
        "openrouter": settings.OPENROUTER_API_KEY,
        "google": settings.GOOGLE_API_KEY,
    }

    print("Seeding API keys into the database...")

    for provider, key_value in keys_to_seed.items():
        if not key_value:
            print(f"Skipping '{provider}' key: not found in .env file.")
            continue

        # Check if a key for this provider already exists
        exists = db.query(APIKey).filter(APIKey.provider == provider).first()
        if exists:
            print(f"Key for provider '{provider}' already exists in the database. Skipping.")
        else:
            # Encrypt the key before storing
            encrypted_key = cipher.encrypt(key_value.encode()).decode()
            
            new_key = APIKey(
                provider=provider,
                encrypted_key=encrypted_key,
                is_active=True
            )
            db.add(new_key)
            print(f"Adding new key for provider '{provider}'.")

    db.commit()
    db.close()
    print("API key seeding complete.")

if __name__ == "__main__":
    seed_api_keys()