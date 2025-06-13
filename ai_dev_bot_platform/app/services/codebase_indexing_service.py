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
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
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
        index.add(np.array([embedding]))  # FAISS expects a 2D array

        # Store metadata associated with this vector's index in FAISS
        self.project_metadata[project_id].append(
            {
                "file_path": file_path,
                "text_chunk": text_chunk,
                "faiss_index": index.ntotal - 1,
            }
        )
        logger.info(
            f"Indexed chunk for {file_path} into project {project_id}. Index size: {index.ntotal}"
        )
        return {"status": "indexed", "file_path": file_path, "chunks": 1}

    async def index_directory(self, project_id: str, directory_path: str):
        """Index all files in a directory recursively"""
        # Implementation would walk through the directory and index each file
        # For now, return a success message
        return {"status": "directory_indexed", "directory": directory_path}

    async def query_codebase(
        self, project_id: str, query: str, top_k: int = 3
    ) -> List[Dict]:
        """Query the codebase index for relevant code snippets"""
        logger.info(
            f"Querying codebase for project {project_id} with query: {query[:50]}..."
        )
        if project_id not in self.project_indexes:
            logger.warning(
                f"No index found for project {project_id}. Returning empty results."
            )
            return []

        index = self.project_indexes[project_id]
        if index.ntotal == 0:
            logger.info(f"Index for project {project_id} is empty.")
            return []

        query_embedding = await self.generate_embedding(query)
        distances, indices = index.search(
            np.array([query_embedding]), k=min(top_k, index.ntotal)
        )

        results = []
        project_meta = self.project_metadata[project_id]
        for i in range(len(indices[0])):
            faiss_idx = indices[0][i]
            if faiss_idx < len(project_meta):
                meta_item = project_meta[faiss_idx]
                results.append(
                    {
                        "file_path": meta_item["file_path"],
                        "content_chunk": meta_item["text_chunk"],
                        "similarity_score": 1 - distances[0][i],
                    }
                )
            else:
                logger.warning(
                    f"FAISS index {faiss_idx} out of bounds for project_meta with length {len(project_meta)}"
                )

        logger.info(f"Query returned {len(results)} results.")
        return results

    async def generate_embedding(self, text: str) -> np.ndarray:  # Return numpy array
        """Generate embedding for text using an embedding model"""
        try:
            logger.debug(
                f"Generating embedding for text chunk starting with: {text[:50]}...",
                extra={"text_sample": text[:100]},
            )
            # SentenceTransformer works synchronously, wrap if true async needed elsewhere
            embedding = self.embedding_model.encode(
                text, convert_to_tensor=False
            )  # Get numpy array
            return embedding.astype("float32")  # FAISS typically wants float32
        except Exception as e:
            logger.error(
                "Error generating embedding",
                exc_info=True,
                extra={"text_sample": text[:100], "error": str(e)},
            )
            raise  # Re-raise to let caller handle

    def _get_or_create_project_index(
        self, project_id: str, embedding_dim: int = 384
    ) -> faiss.Index:  # all-MiniLM-L6-v2 is 384-dim
        if project_id not in self.project_indexes:
            logger.info(
                f"Creating new FAISS index for project {project_id} with dim {embedding_dim}"
            )
            # Using IndexFlatL2, a simple L2 distance index.
            # For larger datasets, more complex indexes like IndexIVFFlat might be better.
            index = faiss.IndexFlatL2(embedding_dim)
            self.project_indexes[project_id] = index
            self.project_metadata[project_id] = []
        return self.project_indexes[project_id]


# Singleton instance for the service
# codebase_indexing_service = CodebaseIndexingService(APIKeyManager())
