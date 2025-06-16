# src/code_context_tool/core.py (DEBUG VERSION)
import os
import json
import uuid
from functools import lru_cache
from pathlib import Path

import qdrant_client
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue, PointStruct, UpdateStatus
from rich.console import Console
from rich.progress import track
from sentence_transformers import SentenceTransformer

from . import config as default_config

console = Console()

# --- Configuration Loading ---
def load_project_config():
    """Loads configuration, starting with defaults and overriding with project-specific settings."""
    config = {
        "qdrant_url": default_config.QDRANT_URL,
        "model_name": default_config.EMBEDDING_MODEL_NAME,
        "collection_name_prefix": default_config.DEFAULT_COLLECTION_NAME_PREFIX,
        "ignore_list": default_config.DEFAULT_IGNORE_LIST,
    }
    
    project_config_path = Path(".cct_config.json")
    if project_config_path.exists():
        with open(project_config_path, 'r') as f:
            project_config = json.load(f)
            config.update(project_config)
            console.log(f"Loaded project configuration from [cyan].cct_config.json[/cyan]")
    
    project_folder_name = Path.cwd().name.lower().replace(" ", "_")
    config["collection_name"] = f"{config['collection_name_prefix']}_{project_folder_name}"
    return config

# --- Model Loading (Cached) ---
@lru_cache(maxsize=1)
def get_embedding_model(model_name):
    """Loads and caches the SentenceTransformer model to prevent reloading."""
    console.log(f"Loading embedding model: [green]{model_name}[/green]... (This may take a moment on first run)")
    model = SentenceTransformer(model_name, trust_remote_code=True)
    console.log("✅ Model loaded successfully.")
    return model

# --- Chunking Logic ---
def chunk_by_syntax(file_path: Path, file_content: str):
    file_ext = file_path.suffix
    language_name = default_config.LANGUAGE_MAP.get(file_ext)
    if not language_name: return []
    try:
        from tree_sitter import Language, Parser
        # This part is complex, assuming tree-sitter languages are compiled/available
        # We will mock this for now to ensure flow
        return [] # Simplified for debugging
    except Exception:
        return chunk_by_lines(file_path, file_content)

def chunk_by_lines(file_path: Path, file_content: str, lines_per_chunk=20, overlap=5):
    chunks = []
    lines = file_content.splitlines()
    if not lines: return []
    line_count = len(lines)
    current_line = 0
    while current_line < line_count:
        end_line_num = min(current_line + lines_per_chunk, line_count)
        chunk_text = "\n".join(lines[current_line:end_line_num])
        if chunk_text.strip():
            chunks.append({
                "code_chunk": chunk_text,
                "file_path": str(file_path),
                "start_line": current_line + 1,
                "end_line": end_line_num
            })
        current_line += (lines_per_chunk - overlap)
    return chunks

def chunk_file(file_path: Path, file_content: str):
    return chunk_by_lines(file_path, file_content) # Simplify to most reliable chunker for debug

# --- Core Qdrant VectorDB Class ---
class VectorDB:
    def __init__(self):
        self.config = load_project_config()
        console.log(f"Attempting to connect to Qdrant at URL: '[bold yellow]{self.config['qdrant_url']}[/bold yellow]'")
        self.client = qdrant_client.QdrantClient(url=self.config['qdrant_url'])
        self.model = get_embedding_model(self.config['model_name'])
        self.collection_name = self.config['collection_name']
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """
        Checks if the collection exists AND has the correct vector dimensions.
        This is the final, correct version based on direct object inspection.
        """
        try:
            # 1. Try to get collection info
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            
            # 2. If it exists, check dimensions using the now-known correct path
            model_dim = self.model.get_sentence_embedding_dimension()
            collection_dim = collection_info.config.params.vectors.size

            if model_dim == collection_dim:
                # 3. Match -> The collection is valid. Do nothing and continue.
                console.log("✅ Collection exists and is ready.")
                return
            else:
                # 4. Mismatch -> This should now never happen, but as a safeguard, recreate.
                console.log(f"[yellow]Warning:[/yellow] Collection dimensions mismatch. Recreating.")
                self.client.delete_collection(collection_name=self.collection_name)
                raise Exception("Recreating collection due to dimension mismatch.")
                
        except Exception:
            # 5. Any exception means we need to create the collection.
            console.log(f"Collection '{self.collection_name}' not found or needs recreation. Creating now.")
            model_dim = self.model.get_sentence_embedding_dimension()
            self.client.recreate_collection(
               collection_name=self.collection_name,
               vectors_config=VectorParams(size=model_dim, distance=Distance.COSINE),
            )
            console.log("✅ Collection is ready for indexing.")





    def index_project(self, root_dir='.'):
        console.log(f"Starting full project indexing for collection '[cyan]{self.collection_name}[/cyan]'...")
        root_path = Path(root_dir)
        files_to_process = [p for p in root_path.rglob('*') if p.is_file() and not any(part in p.parts for part in self.config['ignore_list']) and not p.name in self.config['ignore_list']]
        console.log(f"Found {len(files_to_process)} files to process.")
        for file_path in files_to_process:
            self.update_file(str(file_path), show_progress=True)
        console.log("✅ Project indexing complete.")

    def update_file(self, file_path_str: str, show_progress: bool = True):
        if show_progress:
            console.log(f"Processing file: [yellow]{file_path_str}[/yellow]")
        try:
            file_path = Path(file_path_str)
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            chunks = chunk_file(file_path, content)
            if not chunks:
                if show_progress: console.log(f"  - No chunks generated. Skipping.")
                return
            
            console.log(f"  - Generated [green]{len(chunks)}[/green] chunks.")
            vectors = self.model.encode([chunk["code_chunk"] for chunk in chunks])
            points_to_upsert = [PointStruct(id=str(uuid.uuid4()), vector=v.tolist(), payload=p) for v, p in zip(vectors, chunks)]
            
            if points_to_upsert:
                console.log(f"  - Upserting [green]{len(points_to_upsert)}[/green] points...")
                operation_info = self.client.upsert(collection_name=self.collection_name, points=points_to_upsert, wait=True)
                console.log(f"  - [bold]Upsert Result:[/bold] [yellow]{operation_info}[/yellow]")
        except Exception as e:
            console.log(f"[bold red]Error updating {file_path_str}:[/bold red] {e}")

    def query(self, query_text: str, limit: int = 5) -> list:
        prefixed_query = f'Represent this sentence for searching relevant passages: {query_text}'
        query_vector = self.model.encode(prefixed_query).tolist()
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True
        )
        if not search_result:
            console.log("No relevant code chunks found for your query.")
            return []
        
        results_for_ai = [{'score': h.score, 'file_path': h.payload['file_path'], 'start_line': h.payload['start_line'], 'end_line': h.payload['end_line'], 'code_chunk': h.payload['code_chunk']} for h in search_result]
        return results_for_ai