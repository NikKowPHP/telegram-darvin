import logging
import os
from typing import Optional, List
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

# Define the base path for our local storage
LOCAL_STORAGE_BASE_PATH = "local_storage"

class StorageService:
    def __init__(self):
        self.client: Optional[Client] = None
        self.is_local_mode = False

        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                logger.info("Supabase client initialized for StorageService (Cloud Mode).")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client, falling back to local mode: {e}", exc_info=True)
                self.is_local_mode = True
        else:
            # If no Supabase credentials, we explicitly switch to local mode
            self.is_local_mode = True
            logger.info("StorageService initialized in Local Mode. Files will be stored in './local_storage'.")
            # Ensure the base directory exists
            os.makedirs(LOCAL_STORAGE_BASE_PATH, exist_ok=True)

    def upload_file(self, bucket_name: str, file_path: str, file_content: str) -> bool:
        if self.is_local_mode:
            return self._local_upload(bucket_name, file_path, file_content)
        
        # --- Supabase Logic (unchanged) ---
        if not self.client:
            logger.error("Storage client not initialized. Cannot upload file.")
            return False
        try:
            # Note: Supabase's from_ is now from_
            self.client.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content.encode('utf-8'),
                file_options={"content-type": "text/plain;charset=utf-8", "upsert": "true"}
            )
            logger.info(f"Successfully uploaded {file_path} to Supabase bucket {bucket_name}.")
            return True
        except Exception as e:
            logger.error(f"Failed to upload {file_path} to Supabase Storage: {e}", exc_info=True)
            return False

    def download_file(self, bucket_name: str, file_path: str) -> Optional[str]:
        if self.is_local_mode:
            return self._local_download(bucket_name, file_path)
            
        # --- Supabase Logic (unchanged) ---
        if not self.client:
            logger.error("Storage client not initialized. Cannot download file.")
            return None
        try:
            response = self.client.storage.from_(bucket_name).download(path=file_path)
            logger.info(f"Successfully downloaded {file_path} from Supabase bucket {bucket_name}.")
            return response.decode('utf-8')
        except Exception as e:
            logger.warning(f"Failed to download {file_path} from Supabase Storage: {e}")
            return None

    def create_bucket(self, bucket_name: str) -> bool:
        if self.is_local_mode:
            return self._local_create_bucket(bucket_name)

        # --- Supabase Logic (unchanged) ---
        if not self.client:
            logger.error("Storage client not initialized. Cannot create bucket.")
            return False
        try:
            self.client.storage.create_bucket(bucket_name)
            logger.info(f"Successfully created Supabase bucket: {bucket_name}")
            return True
        except Exception as e:
            if "Bucket already exists" in str(e):
                logger.warning(f"Supabase bucket '{bucket_name}' already exists. Skipping creation.")
                return True
            logger.error(f"Failed to create Supabase bucket {bucket_name}: {e}", exc_info=True)
            return False

    def list_files(self, bucket_name: str) -> List[dict]:
        if self.is_local_mode:
            return self._local_list_files(bucket_name)

        # --- Supabase Logic (unchanged) ---
        if not self.client:
            logger.error("Storage client not initialized. Cannot list files.")
            return []
        try:
            return self.client.storage.from_(bucket_name).list()
        except Exception as e:
            logger.error(f"Failed to list files for Supabase bucket {bucket_name}: {e}", exc_info=True)
            return []

    # --- Local Storage Helper Methods ---

    def _local_create_bucket(self, bucket_name: str) -> bool:
        try:
            bucket_path = os.path.join(LOCAL_STORAGE_BASE_PATH, bucket_name)
            os.makedirs(bucket_path, exist_ok=True)
            logger.info(f"Local bucket '{bucket_name}' created/ensured at: {bucket_path}")
            return True
        except OSError as e:
            logger.error(f"Failed to create local bucket '{bucket_name}': {e}", exc_info=True)
            return False
    
    def _local_upload(self, bucket_name: str, file_path: str, file_content: str) -> bool:
        try:
            # Ensure the bucket (directory) exists
            self._local_create_bucket(bucket_name)
            
            full_path = os.path.join(LOCAL_STORAGE_BASE_PATH, bucket_name, file_path)
            
            # Ensure any subdirectories in the file_path also exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            logger.info(f"Successfully saved local file: {full_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload local file to {full_path}: {e}", exc_info=True)
            return False

    def _local_download(self, bucket_name: str, file_path: str) -> Optional[str]:
        full_path = os.path.join(LOCAL_STORAGE_BASE_PATH, bucket_name, file_path)
        if not os.path.exists(full_path):
            logger.warning(f"Local file not found for download: {full_path}")
            return None
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to download local file from {full_path}: {e}", exc_info=True)
            return None

    def _local_list_files(self, bucket_name: str) -> List[dict]:
        bucket_path = os.path.join(LOCAL_STORAGE_BASE_PATH, bucket_name)
        if not os.path.isdir(bucket_path):
            return []
        
        files_list = []
        for root, _, files in os.walk(bucket_path):
            for name in files:
                # We need to return a path relative to the bucket root
                relative_path = os.path.relpath(os.path.join(root, name), bucket_path)
                # Mimic Supabase's output format
                files_list.append({"name": relative_path})
        return files_list