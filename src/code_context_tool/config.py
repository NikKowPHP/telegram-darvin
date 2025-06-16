# src/code_context_tool/config.py
import os

# --- DEFAULT CONFIGURATION ---
# These values serve as the base and can be overridden by a project-specific
# .cct_config.json file for tailored behavior.

# The Qdrant instance URL. It's best practice to use an environment variable
# for this, but we provide a common local default.
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# The default embedding model. BAAI/bge-large-en-v1.5 is a top-tier open-source
# model on the MTEB leaderboard, excellent for code retrieval and semantic search.
# Sentence-Transformers will download and cache it locally on first use.
# EMBEDDING_MODEL_NAME = "BAAI/bge-large-en-v1.5"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
# The default collection name prefix. The final name will be derived from the
# project's root folder name to ensure isolation between projects.
DEFAULT_COLLECTION_NAME_PREFIX = "cct"

# A comprehensive list of files, directories, and patterns to ignore during indexing.
# This prevents cluttering the vector database with irrelevant or binary content.
DEFAULT_IGNORE_LIST = [
    '.git',
    '.svn',
    'node_modules',
    '.vscode',
    'dist',
    'build',
    '.DS_Store',
    '__pycache__',
    '*.pyc',
    '*.egg-info',
    'venv',
    '.venv',
    'target',
    'package-lock.json',
    'yarn.lock',
    'poetry.lock',
    'repomix-output.xml',
    '*.log',
]

# Mapping of file extensions to their corresponding tree-sitter language names.
# This is crucial for the syntax-aware chunker.
# Add more languages here as needed.
LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".cpp": "cpp",
    ".cs": "c_sharp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
}

# The node types that tree-sitter will use to create semantic chunks.
# This list targets high-level structures like functions and classes, which provide
# excellent context for retrieval.
SYNTAX_CHUNK_NODE_TYPES = [
    "function_definition",
    "class_definition",
    "function_declaration",
    "method_definition",
    "interface_declaration",
    "struct_declaration",
    "enum_declaration",
]