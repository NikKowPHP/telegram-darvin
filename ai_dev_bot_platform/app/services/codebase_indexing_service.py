import os
import logging
from typing import Dict, List, Optional
from app.core.config import settings
from app.services.api_key_manager import APIKeyManager
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

logger = logging.getLogger(__name__)

class CodebaseIndexingService:
    def __init__(self, api_key_manager: APIKeyManager):
        self.api_key_manager = api_key_manager
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.project_indexes: Dict[str, Optional[faiss.Index]] = {}
        self.project_metadata: Dict[str, List[Dict[str, str]]] = {}

    async def initialize_index(self, project_id: str):
        """Initialize the vector database index for a project"""
        logger.info(f"Initializing codebase index for project {project_id}")
        # Implementation would connect to vector DB (FAISS, Pinecone, etc.)
        # For now, we'll just set a flag
        self.index_initialized = True
        return {"status": "initialized", "project_id": project_id}

    async def index_file(self, project_id: str, file_path: str, content: str):
        """Index a single file in the codebase"""
        if not self.index_initialized:
            await self.initialize_index(project_id)
        
        logger.info(f"Indexing file: {file_path} for project {project_id}")
        # Generate embeddings for the file content
        # In a real implementation, we'd split the file into chunks
        # and generate embeddings for each chunk
        embedding = await self.generate_embedding(content)
        
        # Store embedding in vector DB with metadata
        # self.vector_db.add_embedding(embedding, metadata={"file_path": file_path})
        return {"status": "indexed", "file_path": file_path}

    async def index_directory(self, project_id: str, directory_path: str):
        """Index all files in a directory recursively"""
        # Implementation would walk through the directory and index each file
        # For now, return a success message
        return {"status": "directory_indexed", "directory": directory_path}

    async def query_codebase(self, project_id: str, query: str, top_k: int = 5) -> List[Dict]:
        """Query the codebase index for relevant code snippets"""
        if not self.index_initialized:
            await self.initialize_index(project_id)
        
        # Generate embedding for the query
        query_embedding = await self.generate_embedding(query)
        
        # Query the vector DB for similar embeddings
        # results = self.vector_db.query(query_embedding, top_k=top_k)
        # Placeholder results
        results = [
            {"file_path": "app/main.py", "similarity": 0.92, "content": "from fastapi import FastAPI..."},
            {"file_path": "app/services/user_service.py", "similarity": 0.87, "content": "def get_user_by_telegram_id(...)"}
        ]
        return results

    async def generate_embedding(self, text: str) -> np.ndarray: # Return numpy array
        """Generate embedding for text using an embedding model"""
        logger.debug(f"Generating embedding for text chunk starting with: {text[:50]}...")
        # SentenceTransformer works synchronously, wrap if true async needed elsewhere
        embedding = self.embedding_model.encode(text, convert_to_tensor=False) # Get numpy array
        return embedding.astype('float32') # FAISS typically wants float32

# Singleton instance for the service
# codebase_indexing_service = CodebaseIndexingService(APIKeyManager())