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

    async def index_file_content(self, project_id: str, file_path: str, content: str):
        """Index content for a file in the codebase"""
        logger.info(f"Indexing content for file: {file_path} for project {project_id}")
        # Simple chunking strategy (can be improved, e.g., by lines, by function/class)
        # For now, let's assume content is small enough to be one chunk
        text_chunk = content
        embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        index = self._get_or_create_project_index(project_id, embedding_dim)

        embedding = await self.generate_embedding(text_chunk)
        index.add(np.array([embedding])) # FAISS expects a 2D array
        
        # Store metadata associated with this vector's index in FAISS
        self.project_metadata[project_id].append({
            "file_path": file_path,
            "text_chunk": text_chunk,
            "faiss_index": index.ntotal - 1
        })
        logger.info(f"Indexed chunk for {file_path} into project {project_id}. Index size: {index.ntotal}")
        return {"status": "indexed", "file_path": file_path, "chunks": 1}

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

    def _get_or_create_project_index(self, project_id: str, embedding_dim: int = 384) -> faiss.Index: # all-MiniLM-L6-v2 is 384-dim
        if project_id not in self.project_indexes:
            logger.info(f"Creating new FAISS index for project {project_id} with dim {embedding_dim}")
            # Using IndexFlatL2, a simple L2 distance index.
            # For larger datasets, more complex indexes like IndexIVFFlat might be better.
            index = faiss.IndexFlatL2(embedding_dim)
            self.project_indexes[project_id] = index
            self.project_metadata[project_id] = []
        return self.project_indexes[project_id]

# Singleton instance for the service
# codebase_indexing_service = CodebaseIndexingService(APIKeyManager())