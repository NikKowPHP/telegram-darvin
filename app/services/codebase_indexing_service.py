# ROO-AUDIT-TAG :: feature-004-codebase-indexing.md :: Create codebase indexing service
import faiss
import numpy as np
from typing import List, Dict
from app.core.config import settings

class CodebaseIndexingService:
    """Service for indexing and searching codebases using FAISS."""
    
    def __init__(self):
        self.index = None
        self.code_vectors = []
        self.code_metadata = []
        
    def index_codebase(self, code_files: List[Dict]) -> None:
        """Index a collection of code files."""
        # ROO-AUDIT-TAG :: feature-004-codebase-indexing.md :: Implement code parsing and vectorization
        vectors = [self._code_to_vector(file['content']) for file in code_files]
        self.code_vectors = vectors
        self.code_metadata = code_files
        
        # Create FAISS index
        dimension = len(vectors[0]) if vectors else 0
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(vectors))
        
    def search_codebase(self, query: str, k: int = 5) -> List[Dict]:
        """Search the codebase for similar code snippets."""
        query_vector = self._code_to_vector(query)
        distances, indices = self.index.search(np.array([query_vector]), k)
        
        return [{
            'file': self.code_metadata[i]['path'],
            'content': self.code_metadata[i]['content'],
            'score': float(distances[0][j])
        } for j, i in enumerate(indices[0])]
        
    def update_index(self, file_path: str, new_content: str) -> None:
        """Update the index with new file content."""
        # ROO-AUDIT-TAG :: feature-004-codebase-indexing.md :: Add file change detection
        new_vector = self._code_to_vector(new_content)
        # Update logic would go here
        
    def _code_to_vector(self, code: str) -> List[float]:
        """Convert code to vector representation using AST analysis."""
        import ast
        from collections import defaultdict
        
        # Parse AST and extract features
        tree = ast.parse(code)
        features = defaultdict(int)
        
        # Count different node types
        for node in ast.walk(tree):
            features[type(node).__name__] += 1
            
        # Normalize feature counts
        total_nodes = sum(features.values())
        if total_nodes == 0:
            return [0.0] * 128
            
        # Create normalized vector of AST node frequencies
        vector = []
        for node_type in sorted(features.keys()):
            vector.append(features[node_type] / total_nodes)
            
        # Pad or truncate to 128 dimensions
        return (vector + [0.0] * 128)[:128]

# ROO-AUDIT-TAG :: feature-004-codebase-indexing.md :: END