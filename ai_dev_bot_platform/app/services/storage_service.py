import logging
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.client: Optional[Client] = None
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                logger.info("Supabase client initialized for StorageService.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)

    def upload_file(self, bucket_name: str, file_path: str, file_content: str) -> bool:
        if not self.client:
            logger.error("Storage client not initialized. Cannot upload file.")
            return False
        try:
            self.client.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content.encode('utf-8'),
                file_options={"content-type": "text/plain;charset=utf-8", "upsert": "true"}
            )
            logger.info(f"Successfully uploaded {file_path} to bucket {bucket_name}.")
            return True
        except Exception as e:
            logger.error(f"Failed to upload {file_path} to Supabase Storage: {e}", exc_info=True)
            return False

    def download_file(self, bucket_name: str, file_path: str) -> Optional[str]:
        if not self.client:
            logger.error("Storage client not initialized. Cannot download file.")
            return None
        try:
            response = self.client.storage.from_(bucket_name).download(path=file_path)
            logger.info(f"Successfully downloaded {file_path} from bucket {bucket_name}.")
            return response.decode('utf-8')
        except Exception as e:
            # Supabase client often raises a generic Exception if file not found
            logger.warning(f"Failed to download {file_path} from Supabase Storage: {e}")
            return None