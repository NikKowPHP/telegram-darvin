# ROO-AUDIT-TAG :: refactoring-epic-002-persistent-indexing.md :: Refactor CodebaseIndexingService to use pgvector
import logging
import httpx
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
from app.models.embedding import ProjectEmbedding
from app.core.config import settings

logger = logging.getLogger(__name__)


class CodebaseIndexingService:

    async def _get_embedding_from_service(self, text: str) -> Optional[List[float]]:
        """Call external embedding service to generate vector"""
        EMBEDDING_SERVICE_URL = settings.EMBEDDING_SERVICE_URL
        if not EMBEDDING_SERVICE_URL:
            logger.warning(
                "EMBEDDING_SERVICE_URL is not set. Cannot generate embeddings."
            )
            return None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    EMBEDDING_SERVICE_URL, json={"text": text}, timeout=60.0
                )
                response.raise_for_status()
                return response.json().get("embedding")
        except Exception as e:
            logger.error(f"Failed to get embedding from service: {e}")
            return None

    async def _chunk_content(self, content: str, chunk_size: int = 2000) -> List[str]:
        """Split content into manageable chunks for embedding"""
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunks.append(content[i : i + chunk_size])
        return chunks

    async def index_file_content(
        self, db: Session, project_id: str, file_path: str, content: str
    ):
        """Index content for a file in the codebase"""
        logger.info(f"Indexing content for file: {file_path} in project {project_id}")

        # Chunk the content
        chunks = await self._chunk_content(content)
        success_count = 0

        for i, chunk in enumerate(chunks):
            embedding_vector = await self._get_embedding_from_service(chunk)
            if embedding_vector:
                new_embedding = ProjectEmbedding(
                    project_id=project_id,
                    file_path=file_path,
                    content_chunk=chunk,
                    chunk_index=i,
                    total_chunks=len(chunks),
                    embedding=embedding_vector,
                )
                db.add(new_embedding)
                success_count += 1

        if success_count > 0:
            db.commit()
            logger.info(f"Successfully indexed {success_count} chunks for {file_path}.")
        else:
            logger.error(f"Failed to index any chunks for {file_path}.")

    async def query_codebase(
        self, db: Session, project_id: str, query: str, top_k: int = 3
    ) -> List[Dict]:
        """Query the codebase index for relevant code snippets"""
        logger.info(
            f"Querying codebase for project {project_id} with query: {query[:50]}..."
        )
        query_embedding = await self._get_embedding_from_service(query)
        if not query_embedding:
            return []

        results = (
            db.query(ProjectEmbedding)
            .filter(ProjectEmbedding.project_id == project_id)
            .order_by(ProjectEmbedding.embedding.l2_distance(query_embedding))
            .limit(top_k)
            .all()
        )

        return [
            {
                "file_path": r.file_path,
                "content_chunk": r.content_chunk,
                "chunk_index": r.chunk_index,
                "total_chunks": r.total_chunks,
                "similarity_score": float(
                    ProjectEmbedding.embedding.l2_distance(query_embedding)
                ),
            }
            for r in results
        ]

    async def batch_index_files(
        self, db: Session, project_id: str, files: Dict[str, str]
    ):
        """Index multiple files in a batch"""
        logger.info(f"Batch indexing {len(files)} files for project {project_id}")
        success_count = 0

        for file_path, content in files.items():
            try:
                await self.index_file_content(db, project_id, file_path, content)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to index {file_path}: {e}")
                continue

        return {
            "status": "completed",
            "project_id": project_id,
            "total_files": len(files),
            "success_count": success_count,
        }

    async def rebuild_index(self, db: Session, project_id: str):
        """Rebuild the index for a project from scratch"""
        logger.info(f"Rebuilding index for project {project_id}")
        try:
            # Delete all existing embeddings for this project
            deleted_count = (
                db.query(ProjectEmbedding)
                .filter(ProjectEmbedding.project_id == project_id)
                .delete()
            )
            db.commit()
            return {
                "status": "rebuilt",
                "project_id": project_id,
                "deleted_count": deleted_count,
            }
        except Exception as e:
            logger.error(f"Error rebuilding index for project {project_id}: {e}")
            db.rollback()
            return {"status": "error", "project_id": project_id, "error": str(e)}


# ROO-AUDIT-TAG :: refactoring-epic-002-persistent-indexing.md :: END
