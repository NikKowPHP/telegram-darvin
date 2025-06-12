# Phase 3 Implementation Todo - Codebase Indexing & Verification

**Project Goal:** Implement codebase indexing with FAISS, add verification loop, and basic Aider integration.

## Task 1: Add Dependencies for Codebase Indexing
- [x] **File:** `ai_dev_bot_platform/requirements.txt`
- **Action:** Add these lines:
  ```
  sentence-transformers
  faiss-cpu
  numpy
  ```
- **Verification:** `requirements.txt` contains the new dependencies.

## Task 2: Enhance CodebaseIndexingService
- [x] **File:** `ai_dev_bot_platform/app/services/codebase_indexing_service.py`
- **Actions:**
  1.  Add imports:
     ```python
     from sentence_transformers import SentenceTransformer
     import faiss
     import numpy as np
     ```
  2.  Update `__init__` to initialize embedding model and FAISS indexes:
     ```python
     self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
     self.project_indexes = {}  # {project_id: faiss.Index}
     self.project_metadata = {} # {project_id: List[dict]}
     ```
  3.  Implement `generate_embedding` method:
     ```python
     async def generate_embedding(self, text: str) -> np.ndarray:
         return self.embedding_model.encode(text, convert_to_tensor=False).astype('float32')
     ```
  4.  Add `_get_or_create_project_index` helper:
     ```python
     def _get_or_create_project_index(self, project_id: str, dim: int = 384) -> faiss.Index:
         if project_id not in self.project_indexes:
             index = faiss.IndexFlatL2(dim)
             self.project_indexes[project_id] = index
             self.project_metadata[project_id] = []
         return self.project_indexes[project_id]
     ```
  5.  Implement `index_file_content`:
     ```python
     async def index_file_content(self, project_id: str, file_path: str, content: str):
         index = self._get_or_create_project_index(project_id)
         embedding = await self.generate_embedding(content)
         index.add(np.array([embedding]))
         self.project_metadata[project_id].append({
             "file_path": file_path,
             "content": content,
             "index_id": index.ntotal - 1
         })
     ```
  6.  Implement `query_codebase`:
     ```python
     async def query_codebase(self, project_id: str, query: str, k: int = 3) -> List[dict]:
         index = self.project_indexes.get(project_id)
         if not index or index.ntotal == 0:
             return []
         query_embedding = await self.generate_embedding(query)
         distances, indices = index.search(np.array([query_embedding]), k)
         return [self.project_metadata[project_id][i] for i in indices[0] if i < len(self.project_metadata[project_id])]
     ```
- **Verification:** All methods exist and are properly implemented.

## Task 3: Integrate Indexing in Orchestrator
- [x] **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
- **Actions:**
  1. In `_handle_implement_task`, after creating/updating a project file:
     ```python
     await self.codebase_indexing_service.index_file_content(
         str(project.id),
         implementation["filename"],
         implementation["code"]
     )
     ```
- **Verification:** Orchestrator indexes files after implementation.

## Task 4: Implement Verification Loop
- [x] **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
- **Actions:**
  1. In `_handle_implement_task`, after indexing:
     ```python
     verification_result = await self.architect_agent.verify_implementation_step(
         project=project,
         code_snippet=implementation["code"],
         relevant_docs=project.description,
         todo_item=todo_item
     )
     ```
  2. Handle verification status (APPROVED/REJECTED) and update project state accordingly.
- **Verification:** Architect agent verifies implementations, and orchestrator updates project status.

## Task 5: Basic Aider Integration Stub
- [x] **File:** `ai_dev_bot_platform/app/agents/implementer_agent.py`
- **Action:** Add method:
  ```python
  async def apply_changes_with_aider(self, project_root: str, file_path: str, instruction: str) -> dict:
      return {"status": "stubbed", "output": "Aider integration pending"}
  ```
- **Verification:** Method exists in ImplementerAgent.

## Task 6: Update Master Plan
- **File:** `todos/master_development_plan.md`
- **Action:** Mark Phase 3 as in progress:
  ```markdown
  - [x] **Phase 3: Codebase Indexing & Verification** (in progress)
  ```
- **Verification:** Master plan updated.