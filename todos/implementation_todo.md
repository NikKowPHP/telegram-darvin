Okay, this is an ambitious and excellent goal! Generating a *truly* detailed TODO list for a 4B model to implement the remaining phases (3-6) to "prod condition" requires breaking things down to an almost painful level of granularity. The 4B model will excel at code generation for well-defined functions/classes and file content, but struggle with complex architectural reasoning, subtle bug fixing, or advanced environment setup without extremely precise instructions.

This `implementation_todo.md` will assume:
1.  The fixes from `refactor_and_fix_todo.md` have been successfully applied.
2.  "Roo" (the 4B LLM) is guided by the rules in `.roo/rules-code/rules.md` (or a similar instruction set).
3.  Human supervision is available for review, complex integration, and tasks Roo cannot perform (like actually running `docker build` or `kubectl apply`, or debugging non-obvious errors).
4.  "Prod condition" means the application is containerized, has basic configuration for deployment, and core features are working, but might not include advanced CI/CD, full-scale monitoring dashboards, or hardened security beyond best practices outlined.

---

# `implementation_todo.md` - AI Dev Bot (Phases 3-6)

**Project Goal:** Implement Phases 3-6 of the AI-Powered Development Assistant Bot platform, leading to a production-ready (initial) state.
**Source of Truth for Features & Architecture:** `documentation/high_level_documentation.md` and other supporting documents in `documentation/`.
**Current Project Root:** Assumed to be `ai_dev_bot_platform/`. All paths are relative to this unless specified.

---

## Phase 3: Codebase Indexing, Verification Loop & Basic Aider Integration

**Goal:** Enable context-aware operations by indexing generated code, implement a verification cycle for implemented tasks, and lay groundwork for Aider tool integration.

*   `[x]` **P3.1: Add Dependencies for Codebase Indexing**
    *   Action: Modify `requirements.txt`.
    *   Add the following lines:
        ```
        sentence-transformers
        faiss-cpu # For local FAISS vector index
        # Consider 'numpy' if not pulled in as a sub-dependency by above
        ```
    *   Verification: `requirements.txt` includes `sentence-transformers` and `faiss-cpu`.
    *   Note: Human supervisor should re-install requirements in the virtual environment.

*   `[x]` **P3.2: Enhance `CodebaseIndexingService.__init__`**
    *   File: `app/services/codebase_indexing_service.py`
    *   Action:
        1.  Add import: `from sentence_transformers import SentenceTransformer`.
        2.  Add import: `import faiss` (if available, otherwise note for human).
        3.  Add import: `import numpy as np`.
        4.  Modify `__init__` to:
            *   Initialize `self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')` (or another suitable small model).
            *   Initialize `self.project_indexes: Dict[str, Optional[faiss.Index]] = {}` to store FAISS indexes per project_id.
            *   Initialize `self.project_metadata: Dict[str, List[Dict[str, str]]] = {}` to store metadata (file_path, chunk_text) for each vector.
            *   Remove `self.index_initialized` and `self.llm_client` if not directly used for embeddings here (using SentenceTransformer directly).
    *   Verification: `__init__` method updated with `SentenceTransformer` and FAISS-related attributes.

*   `[x]` **P3.3: Implement `CodebaseIndexingService.generate_embedding` (Actual)**
    *   File: `app/services/codebase_indexing_service.py`
    *   Action: Modify `generate_embedding` method:
        ```python
        async def generate_embedding(self, text: str) -> np.ndarray: # Return numpy array
            logger.debug(f"Generating embedding for text chunk starting with: {text[:50]}...")
            # SentenceTransformer works synchronously, wrap if true async needed elsewhere, but for direct use it's fine.
            embedding = self.embedding_model.encode(text, convert_to_tensor=False) # Get numpy array
            return embedding.astype('float32') # FAISS typically wants float32
        ```
    *   Verification: Method uses `self.embedding_model.encode`.

*   `[x]` **P极3.4: Implement `CodebaseIndexingService._get_or_create_project_index`**
    *   File: `app/services/codebase_indexing_service.py`
    *   Action: Add a new private helper method:
        ```python
        def _get_or_create_project_index(self, project_id:极 str, embedding_dim: int = 384) -> faiss.Index: # all-MiniLM-L6-v2 is 384-dim
            if project_id not in self.project_indexes:
                logger.info(f"Creating new FAISS index for project {project_id} with dim {embedding_dim}")
                # Using IndexFlatL2, a simple L2 distance index.
                # For larger datasets, more complex indexes like IndexIVFFlat might be better.
                index = faiss.IndexFlatL2(embedding_dim)
                self.project_indexes[project_id] = index
                self.project_metadata[project_id] = []
            return self.project_indexes[project_id]
        ```
    *   Verification: Helper method created.

*   `[x]` **P3.5: Implement `CodebaseIndexingService.index_file_content` (Actual)**
    *   File: `app/services/codebase_indexing_service.py`
    *   Action: Remove old `index_file` method. Create a new `index_file_content` method:
        ```python
        async def index_file_content(self, project_id: str, file_path: str, content: str):
            logger.info(f"Indexing content for file: {file_path} for project {project_id}")
            # Simple chunking strategy (can be improved, e.g., by lines, by function/class)
            # For now, let's assume content is small enough to be one chunk, or needs smarter chunking here.
            # For this TODO, we'll treat the whole content as one chunk for simplicity.
            # TODO: Implement smarter text chunking for large files.
            text_chunk = content 
            embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            index = self._get_or_create_project_index(project_id, embedding_dim)

            embedding = await self.generate_embedding(text_chunk)
            index.add(np.array([embedding])) # FAISS expects a 2D array
            
            # Store metadata associated with this vector's index in FAISS
            # The index in FAISS is `index.ntotal - 1` for the newly added vector
            self.project_metadata[project_id].append({
                "file_path": file_path,
                "text_chunk": text_chunk, # Store the actual text for retrieval
                "faiss_index": index.ntotal -1 
            })
            logger.info(f"Indexed chunk for {file_path} into project {project_id}. Index size: {index.ntotal}")
            return {"status": "indexed", "file_path": file_path, "chunks": 1}
        ```
    *   Verification: Method uses `generate_embedding`, `_get_or_create_project_index`, `index.add`, and updates `project_metadata`.

*   `[x]` **P3.6: Implement `CodebaseIndexingService.query_codebase` (Actual)**
    *   File: `app/services/codebase_indexing_service.py`
    *   Action: Modify `query_codebase` (previously `query_index`):
        ```python
        async def query_codebase(self, project_id: str, query: str, top_k: int = 3) -> List[Dict]:
            logger.info(f"Querying codebase for project {project_id} with query: {query[:50]}...")
            if project_id not in self.project_indexes:
                logger.warning(f"No index found for project {project_id}. Returning empty results.")
                return []

            index = self.project_indexes[project_id]
            if index.ntotal == 0:
                logger.info(f"Index for project {project_id} is empty.")
                return []

            query_embedding = await self.generate_embedding(query)
            distances, indices = index.search(np.array([query_embedding]), k=min(top极_k, index.ntotal))
            
            results = []
            project_meta = self.project_metadata[project_id]
            for i in range(len(indices[0])):
                faiss_idx = indices[0][i]
                # Find the metadata entry that corresponds to this faiss_idx
                # This assumes metadata is stored in the order vectors were added. A safer way
                # would be to ensure project_meta items have a direct link or are queryable by faiss_idx
                # For now, we search. A better way: self.project_metadata could be a dict mapping faiss_index to metadata.
                # Or, ensure metadata is appended in sync with faiss index additions.
                # Let's assume project_meta[faiss_idx] is the correct metadata. (Requires careful management)
                
                # Simplified assumption: iterate through metadata to find the matching faiss_idx
                # This is inefficient for large metadata lists.
                # A better approach would be `metadata_item = project_meta[faiss_idx]` if `project_meta`
                # was structured as a list that directly maps to FAISS indices.
                # Given our current append-only metadata, this is a risk.
                # Let's refine: find the metadata item whose 'faiss_index' matches.
                # This is still not ideal. The mapping needs to be robust.
                # For this exercise, we'll assume a simple list structure and hope it maps correctly.
                # In a real system, a proper mapping is crucial.
                
                # Corrected approach: find metadata by the 'faiss_index' key stored in metadata
                # This still assumes that self.project_metadata[project_id] is a list of dicts,
                # and each dict has a 'faiss_index' field.
                
                # Let's assume self.project_metadata[project_id] is a list of dicts,
                # and each dict is {"file_path": ..., "text_chunk": ..., "original_faiss_index_at_add_time": ...}
                # We need to retrieve based on the indices returned by faiss.search
                
                # For this TODO, let's retrieve using the direct index from FAISS search results.
                # This implies self.project_metadata[project_id] must be ordered exactly as vectors in FAISS.
                if faiss_idx < len(project_meta):
                    meta_item = project_meta[faiss_idx]
                    results.append({
                        "file_path": meta_item["file_path"],
                        "content_chunk": meta_item["text_chunk"], # Return the text
                        "similarity_score": 1 - distances[0][i] # L2 distance, convert to similarity (0-1 range often not guaranteed)
                                                              # Or just return distance: "distance": distances[0][i]
                    })
                else:
                    logger.warning(f"FAISS index {faiss_idx} out of bounds for project_meta with length {len(project_meta)}")

            logger.info(f"Query returned {len(results)} results.")
            return results
        ```
    *   Verification: Method uses `generate_embedding`, `index.search`, and retrieves metadata to form results.

*   `[x]` **P3.7: Integrate Indexing in `ModelOrchestrator`**
    *   File: `app/services/orchestrator_service.py`
    *   Action:
        1.  In `__init__`, ensure `self.codebase_indexing_service = CodebaseIndexingService(self.api_key_manager)` is initialized. (Already there from `refactor_and_fix_todo.md` if applied).
        2.  Modify `_handle_implement_task`:
            *   After `self.project_file_service.create_project_file(...)`:
                ```python
                # Index the newly created/updated file
                await self.codebase_indexing_service.index_file_content(
                    project_id=str(project.id), # Ensure project_id is string
                    file_path=implementation["filename"],
                    content=implementation["code"]
                )
                ```
    *   Verification: Orchestrator calls `index_file_content` after a file is created/updated by implementer.

*   `[x]` **P3.8: Implement Verification Loop in `ModelOrchestrator`**
    *   File: `app/services/orchestrator_service.py`
    *   Action: Modify `_handle_implement_task` further:
        *   After indexing the file (from P3.7), add the verification call:
            ```python
            # ... after indexing ...
            logger.info(f"Requesting verification for task: {todo_item} of project {project.id}")
            
            # Prepare relevant docs for verification (simplified for now)
            # In future, this could be specific design docs or related code.
            relevant_docs_for_verification = project.description # Or architect_agent's generated docs
            if project.current_todo_markdown: # Use the plan itself as part of context
                 relevant_docs_for_verification += "\n\n## Current TODO Plan:\n" + project.current_todo_markdown

            verification_result = await self.architect_agent.verify_implementation_step(
                project=project, # Pass the whole project object
                code_snippet=implementation["code"],
                relevant_docs=relevant_docs_for_verification,
                todo_item=todo_item
            )

            verification_status = verification_result.get("status", "ERROR")
            verification_feedback = verification_result.get("feedback", "极No feedback provided.")

            if verification_status == "APPROVED":
                # Mark TODO item as [x]
                new_todo_markdown = project.current_todo_markdown.replace(f"[ ] {todo_item}", f"[x] {todo_item}", 1)
                updated_project_status = "implementing" # Or "verifying_next_task"
                
                # Check if all tasks are done
                if "[ ]" not in new_todo_markdown:
                    updated_project_status = "verification_complete" # A new status before final README
                    logger.info(f"All tasks completed for project {project.id}")
                
                self.project_service.update_project(self.db, project.id, ProjectUpdate(
                    current_todo_markdown=new_todo_markdown,
                    status=updated_project_status
                ))
                
                return (
                    f"Task '{todo_item}' implemented AND VERIFIED!\n"
                    f"File: {implementation.get('filename', 'N/A')}\n"
                    f"Architect Feedback: {verification_feedback}\n"
                    f"Project status: {updated_project_status}. Next steps..."
                )
            elif verification_status == "REJECTED":
                # Do not mark TODO as complete.
                # Potentially add architect's feedback as a new sub-task or comment in TODO
                # For now, just inform user.
                self.project_service.update_project(self.db, project.id, ProjectUpdate(status="awaiting_refinement"))
                return (
                    f"Task '{todo_item}' implemented but REJECTED by Architect.\n"
                    f"File: {implementation.get('filename', 'N/A')}\n"
                    f"Architect Feedback: {verification_feedback}\n"
                    f"Please review the feedback and consider refining the task or providing more details."
                )
            else: // ERROR case
                return (
                    f"Error during verification of task '{todo_item}'.\n"
                    f"Feedback: {verification_feedback}"
                )
            ```
    *   Modify the end of `_handle_implement_task` to remove the old success message if verification logic is added before it. The return should now come from within the verification conditional blocks.
    *   Verification: Orchestrator calls `verify_implementation_step`, updates project status and TODO based on "APPROVED"/"REJECTED".

*   `[x]` **P3.9: Pass Code Context from Index to `ImplementerAgent`**
    *   File: `app/agents/implementer_agent.py`
    *   Action: Modify `implement_todo_item` method signature and logic:
        1.  Add `project_id: str` and `codebase_indexer: CodebaseIndexingService` to parameters.
        2.  Inside the method, before crafting the prompt:
            ```python
            # Get relevant code context
            if codebase_indexer:
                logger.debug(f"Implementer querying codebase for context related to: {todo_item}")
                context_snippets = await codebase_indexer.query_codebase(project_id=project_id, query=todo_item, top_k=2)
                relevant_code = "\n---\n".join([f"File: {s['file_path']}\n```\n{s['content_chunk']}\n```" for s in context_snippets])
                if not relevant_code:
                    relevant_code = "No specific relevant code snippets found in the current codebase."
            else:
                relevant_code = "Codebase indexing service not available."
            ```
        3.  Ensure `relevant_code` is used in the prompt.
    *   File: `app/services/orchestrator_service.py`
    *   Action: Modify `_handle_implement_task` method:
        1.  When calling `self.implementer_agent.implement_todo_item`, pass `project_id=str(project.id)` and `codebase_indexer=self.codebase_indexing_service`.
    *   Verification: Implementer agent uses `query_codebase` to fetch context. Orchestrator passes necessary arguments.

*   `[x]` **P3.10: Basic Aider Integration Stub (Conceptual)**
    *   File: `app/agents/implementer_agent.py`
    *   Action: Add a new method stub:
        ```python
        import subprocess
        # ...
        async def apply_changes_with_aider(self, project_root_path: str, file_path: str, instruction: str) -> Dict[str, str]:
            logger.info(f"Attempting to apply changes to {file_path} using Aider: {instruction}")
            # This is a highly simplified stub. Real Aider integration needs:
            # - Aider installed in the environment.
            # - The project files accessible on the filesystem where Aider runs.
            # - Careful command construction and error handling.
            # - Potentially running Aider in a non-interactive mode or scripting its input.
            
            # For now, this is a placeholder for where such logic would go.
            # It's unlikely a 4B model can implement robust Aider interaction without very specific, step-by-step guidance
            # on how Aider CLI works and how to manage its state.

            # Example conceptual command structure (actual commands and flow will be more complex):
            # aider_command = [
            #     "aider",
            #     file_path, # Add file to Aider session
            #     "--message", instruction, # Provide the instruction
            #     # Potentially flags for auto-apply, non-interactive, etc.
            # ]
            # Assuming project_root_path is the CWD for Aider
            try:
                # This is a blocking call, for async, use asyncio.create_subprocess_exec
                # result = subprocess.run(aider_command, cwd=project_root_path, capture_output=True, text=True, check=False, timeout=300)
                # if result.returncode == 0:
                #     logger.info(f"Aider command successful. Output: {result.stdout}")
                #     # Need to read the file content after Aider modifies it
                #     # with open(os.path.join(project_root_path, file_path), 'r') as f:
                #     #    updated_content = f.read()
                #     return {"status": "success", "output": result.stdout, "updated_content": "Placeholder: Read file content here"}
                # else:
                #     logger.error(f"Aider command failed. Error: {result.stderr}")
                #     return {"status": "error", "output": result.stderr}
                return {"status": "stubbed", "output": "Aider integration is stubbed."}
            except Exception as e:
                logger.error(f"Exception running Aider: {e}", exc_info=True)
                return {"status": "error", "output": str(e)}
        ```
    *   Verification: Method stub exists.
    *   Note to Human: This task primarily sets up the *location* for Aider logic. Actual, robust Aider scripting is complex.

---

## Phase 4: Monetization & User Management Details

**Goal:** Implement database models and services for tracking costs and credits, integrate credit deduction into the orchestrator, and add basic user-facing credit commands.

*   `[x]` **P4.1: Define `model_pricing` SQLAlchemy Model & Pydantic Schema**
    *   File: `app/models/api_key_models.py` (Consider creating this new file for all API/Billing related models or add to `project.py` or a new `billing.py`)
        *   Action: Create the file or add to an existing one.
        *   Content (for `ModelPricing` from `high_level_documentation.md`):
            ```python
            from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Boolean, TEXT
            from sqlalchemy.sql import func
            from app.db.session import Base # Ensure this is the correct Base

            class ModelPricing(Base):
                __tablename__ = "model_pricing"
                id = Column(Integer, primary_key=True, index=True, autoincrement=True)
                model_provider = Column(String(100), nullable=False) # 'google', 'openrouter'
                model_name = Column(String(255), nullable=False, unique=True) # 'gemini-1.5-pro-latest', 'openrouter/anthropic/claude-3-opus'
                input_cost_per_million_tokens = Column(DECIMAL(12, 6), nullable=False)
                output_cost_per_million_tokens = Column(DECIMAL(12极, 6), nullable=False)
                image_input_cost_per_image = Column(DECIMAL(12, 6), nullable=True)
                image_output_cost_per_image = Column(DECIMAL(12, 6), nullable=True)
                currency = Column(String(10), nullable=False, default='USD')
                notes = Column(TEXT, nullable=True)
                is_active = Column(Boolean, default=True)
                created_at = Column(DateTime, default=func.now())
                updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
            ```
    *   File: `app/schemas/api_key_schemas.py` (or `billing_schemas.py`)
        *   Action: Create or add to.
        *   Content (for `ModelPricing`):
            ```python
            from pydantic import BaseModel
            from typing import Optional
            from decimal import Decimal
            import datetime

            class ModelPricingBase(BaseModel):
                model_provider: str
                model_name: str
                input_cost_per_million_tokens: Decimal
                output_cost_per_million_tokens: Decimal
                image_input_cost_per_image: Optional[Decimal] = None
                image_output_cost_per_image: Optional[Decimal] = None
                currency: str = 'USD'
                notes: Optional[str] = None
                is_active: bool = True

            class ModelPricingCreate(ModelPricingBase):
                pass

            class ModelPricingUpdate(BaseModel): # Allow partial updates
                input_cost_per_million_tokens: Optional[Decimal] = None
                output_cost_per_million_tokens: Optional[Decimal] = None
                # ... other fields that can be updated
                is_active: Optional[bool] = None
                notes: Optional[str] = None


            class ModelPricingInDB(ModelPricingBase):
                id: int
                created_at: datetime.datetime
                updated_at: datetime.datetime
                class Config:
                    from_attributes = True
            ```
    *   Action: Add `from app.models.api_key_models import ModelPricing` (or appropriate path) to `app/db/init_db.py` and have human re-run `init_db.py`.
    *   Verification: Model and schema files created. Table `model_pricing` exists in DB.

*   `[x]` **P4.2: Define `api_key_usage` SQLAlchemy Model & Pydantic Schema**
    *   File: `app/models/api_key_models.py` (or appropriate model file)
    *   Content (for `APIKeyUsage` from `high_level_documentation.md`):
        ```python
        import uuid
        from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
        from sqlalchemy.dialects.postgresql import UUID
        from sqlalchemy.sql import func
        # from app.db.session import Base # Assumed already imported

        class APIKeyUsage(Base):
            __tablename__ = "api_key_usage"
            id = Column(Integer, primary_key=True, index=True, autoincrement=True) # Changed to Integer Serial for simplicity
            project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
            user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
            # api_key_id = Column(Integer, ForeignKey("api_keys.id")) # Assuming an api_keys table exists or will be added
            # For now, let's simplify and not link directly to an api_keys table,
            # as our APIKeyManager loads from env. If keys were in DB, this FK would be important.
            # Let's add a placeholder if we create api_keys table later.
            api_key_identifier: Optional[str] = Column(String(100), nullable=True) # e.g. part of the key or a friendly name

            model_provider = Column(String(100), nullable=False) # 'google', 'openrouter'
            model_name = Column(String(255), nullable=False)
            task_type = Column(String(100), nullable=True) # 'planning', 'coding', 'verification'
            input_tokens_used = Column(Integer, default=0)
            output_tokens_used = Column(Integer, default=0)
            images_processed = Column(Integer, default=0)
            actual_cost_usd = Column(DECIMAL(10, 6), nullable=True)
            response_time_ms = Column(Integer, nullable=True)
            created_at = Column(DateTime, default=func.now())
        ```
    *   File: `app/schemas/api_key_schemas.py` (or appropriate schema file)
    *   Content (for `APIKeyUsage`):
        ```python
        # ... other imports ...
        import uuid # Add if not already imported

        class APIKeyUsageBase(BaseModel):
            project_id: Optional[uuid.UUID] = None
            user_id: Optional[int] = None
            api_key_identifier: Optional[str] = None
            model_provider: str
            model_name:极 str
            task_type: Optional[str] =极 None
            input_tokens_used: int = 0
            output_tokens_used: int = 0
            images_processed: int = 0
            actual_cost_usd: Optional[Decimal] = None
            response_time_ms: Optional[int] = None

        class APIKeyUsageCreate(APIKeyUsageBase):
            pass # All fields provided at creation

        class APIKeyUsageInDB(APIKeyUsageBase):
            id: int
            created_at: datetime.datetime
            class Config:
                from_attributes = True
        ```
    *   Action: Add to `init_db.py` and have human re-run.
    *   Verification: Model and schema files created. Table `api_key_usage` exists.

*   `[x]` **P4.3: Define `credit_transactions` SQLAlchemy Model & Pydantic Schema**
    *   File: `app/models/transaction.py` (new file) or add to `billing.py` or `user.py`
    *   Content (for `CreditTransaction` from `high_level_documentation.md`):
        ```python
        import uuid
        from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, TEXT
        from sqlalchemy.dialects.postgresql import UUID
        from sqlalchemy.sql import func
        from app.db.session import Base

        class CreditTransaction(Base):
            __tablename__ = "credit_transactions"
            id = Column(Integer, primary_key=True, index=True, autoincrement=True) # Simpler PK
            user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
            project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
            api_key_usage_id = Column(Integer, ForeignKey("api_key_usage.id"), nullable=True)
            transaction_type = Column(String(50), nullable=False) # 'initial_grant', 'purchase', 'usage_deduction', etc.
            credits_amount = Column(DECIMAL(10, 2), nullable=False) # Positive for add, negative for deduct
            real_cost_associated_usd = Column(DECIMAL(10, 6), nullable=True)
            external_transaction_id = Column(String(255), nullable=True) # For Stripe, etc.
            description = Column(TEXT, nullable=True)
            created_at = Column(DateTime, default=func.now())
        ```
    *   File: `app/schemas/transaction.py` (new file) or add to `billing_schemas.py` or `user.py`
    *   Content (for `CreditTransaction`):
        ```python
        from pydantic import BaseModel
        from typing import Optional
        from decimal import Decimal
        import datetime
        import uuid

        class CreditTransactionBase(BaseModel):
            user_id: int
            project_id: Optional[uuid.UUID] = None
            api_key_usage_id: Optional[int] = None
            transaction_type: str
            credits_amount: Decimal
            real_cost_associated_usd: Optional[Decimal] = None
            external_transaction_id: Optional[str] = None
            description: Optional[str] = None

        class CreditTransactionCreate(CreditTransactionBase):
            pass

        class CreditTransactionInDB(CreditTransactionBase):
            id: int
            created_at: datetime.datetime
            class Config:
                from_attributes = True
        ```
    *   Action: Add to `init_db.py` and have human re-run.
    *   Verification: Model and schema files created. Table `credit_transactions` exists.

*   `[x]` **P4.4: Create `ModelPricingService`**
    *   File: `app/services/billing_service.py` (new file, or merge services logically)
    *   Action:
        ```python
        from sqlalchemy.orm import Session
        from app.models.api_key_models import ModelPricing # Path to your model
        from app.schemas.api_key_schemas import ModelPricingCreate, ModelPricingUpdate # Path to your schema
        from typing import Optional, List

        class ModelPricingService:
            def get_pricing(self, db: Session, model_provider: str, model_name: str) -> Optional[ModelPricing]:
                return db.query(ModelPricing).filter(
                    ModelPricing.model_provider == model_provider,
                    ModelPricing.model_name == model_name,
                    ModelPricing.is_active == True
                ).first()

            def create_pricing(self, db: Session, pricing_in: ModelPricingCreate) -> ModelPricing:
                db_pricing = ModelPricing(**pricing_in.model_dump())
                db.add(db_pricing)
                db.commit()
                db.refresh(db_pricing)
                return db_pricing
            
            # Add update, list methods if needed for admin
            # Note: Human needs to populate this table with actual pricing data.
        ```
    *   Verification: Service class and methods created.

*   `[x]` **P4.5: Create `APIKeyUsageService`**
    *   File: `app/services/billing_service.py` (or a new `api_usage_service.py`)
    *   Action:
        ```python
        # ... imports ...
        from app.models.api_key_models import APIKeyUsage
        from app.schemas.api_key_schemas import APIKeyUsageCreate
        # ...

        class APIKeyUsageService:
            def log_usage(self, db: Session, usage_in: APIKeyUsageCreate) -> APIKeyUsage:
                db_usage = APIKeyUsage(**usage_in.model_dump())
                db.add(db_usage)
                db.commit()
                db.refresh(db_usage)
                return db_usage
            # Add methods to get usage if needed for reporting
        ```
    *   Verification: Service class and method created.

*   `[x]` **P4.6: Create `CreditTransactionService`**
    *   File: `app/services/billing_service.py` (or a new `transaction_service.py`)
    *   Action:
        ```python
        # ... imports ...
        from app.models.transaction import CreditTransaction # Path to your model
        from app.schemas.transaction import CreditTransactionCreate # Path to your schema
        # ...

        class CreditTransactionService:
            def record_transaction(self, db: Session, transaction_in: CreditTransactionCreate) -> CreditTransaction:
                db_transaction = CreditTransaction(**transaction_in.model_dump())
                db.add(db_transaction)
                db.commit()
                db.refresh(db_transaction)
                return db_transaction
            
            def get_transactions_for_user(self, db: Session, user_id: int) -> List[CreditTransaction]:
                return db.query(CreditTransaction).filter(CreditTransaction.user_id == user_id).order_by(CreditTransaction.created_at.desc()).all()
        ```
    *   Verification: Service class and methods created.

*   `[x]` **P4.7: Enhance `LLMClient` to Return Token Counts and Model Info**
    *   File: `app/utils/llm_client.py`
    *   Action: Modify `call_gemini` and `call_openrouter` to return a dictionary including `text_response`, `input_tokens`, `output_tokens`, `model_name_used`.
        *   For Gemini: Parse `response.usage_metadata` if available (e.g., `response.usage_metadata.prompt_token_count`, `response.usage_metadata.candidates_token_count`).
        *   For OpenRouter: Parse `result.get("usage", {})` (e.g., `result["usage"]["prompt_tokens"]`, `result["usage"]["completion_tokens"]`).
        *   If token counts are not available, return 0 or None for them.
        *   Return structure example: `{"text_response": "...", "input_tokens": X, "output_tokens": Y, "model_name_used": "model/id"}`
    *   Verification: Methods return the enhanced dictionary.

*   `[x]` **P4.8: Implement Credit Deduction in `ModelOrchestrator`**
    *   File: `app/services/orchestrator_service.py`
    *   Action:
        1.  In `__极init__`, instantiate `ModelPricingService`, `APIKeyUsageService`, `CreditTransactionService`.
            ```python
            # In ModelOrchestrator.__init__
            from app.services.billing_service import ModelPricingService, APIKeyUsageService, CreditTransactionService # Adjust path if needed
            from app.services.user_service import update_user_credits # Ensure this exists and is importable
            # ...
            self.model_pricing_service = ModelPricingService()
            self.api_key_usage_service = APIKeyUsageService()
            self.credit_transaction_service = CreditTransactionService()
            # self.user_service = UserService() # If user_service is a class; otherwise use standalone functions
            ```
        2.  Create a new private method `_deduct_credits_for_llm_call`:
            ```python
            from app.schemas.api_key_schemas import APIKeyUsageCreate
            from app.schemas.transaction import CreditTransactionCreate
            from app.core.config import settings
            from decimal import Decimal
            # ...

            async def _deduct_credits_for_llm_call(
                self, 
                user: User, 
                llm_response_data: dict, # The dict from P4.7
                task_type: str,
                project_id: Optional[uuid.UUID] = None
            ):
                model_provider = "google" if "gemini" in llm_response_data.get("model_name_used", "").lower() else "openrouter" # Simple inference
                model_name_used = llm_response_data.get("model_name_used")
                input_tokens = llm_response_data.get("input_tokens", 0)
                output_tokens = llm_response_data.get("output_tokens", 0)

                if not model_name_used:
                    logger.error(f"Cannot deduct credits: model_name_used not found in LLM response data for user {user.id}")
                    return

                pricing = self.model_pricing_service.get_pricing(self.db, model_provider, model_name_used)
                if not pricing:
                    logger.error(f"No pricing found for model {model_provider}/{model_name_used}. Cannot deduct credits for user {user.id}.")
                    # Potentially send a warning to the user or admin
                    return

                actual_cost_usd = (
                    (Decimal(input_tokens) / Decimal(1000000)) * pricing.input_cost_per_million_tokens +
                    (Decimal(output_tokens) / Decimal(1000000)) * pricing.output_cost_per_million_tokens
                )
                
                # Log API usage
                usage_log = APIKeyUsageCreate(
                    user_id=user.id,
                    project_id=project_id,
                    model_provider=model_provider,
                    model_name=model_name_used,
                    task_type=task_type,
                    input_tokens_used=input_tokens,
                    output_tokens_used=output_tokens,
                    actual_cost_usd=actual_cost_usd,
                    # api_key_identifier= ... (if tracking specific key used)
                )
                api_usage_record = self.api_key_usage_service.log_usage(self.db, usage_log)

                # Calculate credits to deduct
                credits_to_deduct = (actual_cost_usd / Decimal(str(settings.PLATFORM_CREDIT_VALUE_USD))) * Decimal(str(settings.MARKUP_FACTOR))
                credits_to_deduct = credits_to_deduct.quantize(Decimal("0.01")) # Round to 2 decimal places

                if credits_to_deduct <= 0: # No cost or negligible
                    logger.info(f"Calculated credits to deduct is {credits_to_deduct} for user {user.id}. No deduction.")
                    return

                # Deduct credits from user
                updated_user = update_user_credits(self.db, user.telegram_user_id, credits_to_deduct, is_deduction=True) # Assuming update_user_credits is importable
                
                if not updated_user:
                    logger.warning(f"Failed to deduct {credits_to_deduct} credits for user {user.id} (insufficient balance or error).")
                    # Handle this scenario - maybe pause project, notify user
                    # For now, log and proceed. This needs robust handling.
                    # We might need to revert the LLM action if credits can't be deducted (complex).
                    return 

                # Record credit transaction
                transaction = CreditTransactionCreate(
                    user_id=user.id,
                    project_id=project_id,
                    api_key_usage_id=api_usage_record.id,
                    transaction_type="usage_deduction",
                    credits_amount=-credits_to_deduct, # Negative for deduction
                    real_cost_associated_usd=actual_cost_usd,
                    description=f"Usage for {task_type} with {model_name_used}"
                )
                self.credit_transaction_service.record_transaction(self.db, transaction)
                logger.info(f"Deducted {credits_to_deduct} credits from user {user.id}. New balance: {updated_user.credit_balance}")
            ```
        3.  Call `_deduct_credits_for_llm_call` after successful LLM calls in `ArchitectAgent` and `ImplementerAgent` logic within the Orchestrator (e.g., in `_handle_new_project` after `architect_agent.generate_initial_plan_and_docs`, and in `_handle_implement_task` after `implementer_agent.implement_todo_item` and `architect_agent.verify_implementation_step`). Pass appropriate `task_type`.
            *   Example in `_handle_new_project` (after successful plan generation):
                ```python
                # llm_response_data should be the dict returned by the LLMClient via ArchitectAgent
                # This needs architect_agent methods to return this detailed dict.
                # For now, let's assume plan_result contains the LLM call details.
                # This part needs careful data plumbing from agent methods.
                # Simplified: if plan_result is the raw LLM response (string), we can't get tokens.
                # Architect/Implementer agent methods need to return the structured dict from LLMClient.
                # Assume plan_result IS that structured dict for this step.
                if "error" not in plan_result and plan_result.get("llm_call_details"): # Assuming agent returns this
                    await self._deduct_credits_for_llm_call(
                        user=user,
                        llm_response_data=plan_result["llm_call_details"],
                        task_type="planning",
                        project_id=project.id
                    )
                ```
    *   **CRITICAL REFACTOR:** `ArchitectAgent` and `ImplementerAgent` methods that call `LLMClient` *must* now return the full dictionary from `LLMClient` (or at least the `text_response` AND the token/model info separately) so the Orchestrator can use it for credit deduction. The Orchestrator should not be parsing raw text to get this.
    *   Verification: Orchestrator attempts to deduct credits. Logs created in `api_key_usage` and `credit_transactions`. User credit balance updated.

*   `[x]` **P4.9: Implement `/status` Command**
    *   File: `app/telegram_bot/handlers.py`
    *   Action: Create `status_command` handler:
        ```python
        from app.services import project_service # Assuming standalone functions or class instance available
        # ...
        async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            user_tg = update.effective_user
            db: Session = SessionLocal()
            try:
                user_db = user_service.get_user_by_telegram_id(db, telegram_user_id=user_tg.id)
                if not user_db:
                    await update.message.reply_text("Please use /start first.")
                    return

                # Get active project (simplified: last created one, or one 'in_progress')
                # This logic needs to be more robust: find project with status 'planning' or 'implementing'
                user_projects = project_service.get_projects_by_user(db, user_id=user_db.id) # Assuming project_service is available
                active_project_info = "No active project."
                current_project_status = "N/A"

                # Find a project that's not completed or failed
                active_project = next((p for p in user_projects if p.status not in ["completed", "failed", "readme_generation"]), None)

                if active_project:
                    active_project_info = f"Current Project: {active_project.title} (ID: {active_project.id})"
                    current_project_status = active_project.status
                
                await update.message.reply_text(
                    f"📊 Your Status 📊\n"
                    f"Credits: {user_db.credit_balance:.2f}\n"
                    f"{active_project_info}\n"
                    f"Project Status: {current_project_status}"
                )
            finally:
                db.close()
        ```
    *   Action: Add `application.add_handler(CommandHandler("status", status_command))` to `bot_main.py`.
    *   Verification: `/status` command shows credit balance and basic project info.

*   `[x]` **P4.10: Implement `/credits` Command (Stub for Purchase)**
    *   File: `app/telegram_bot/handlers.py`
    *   Action: Create `credits_command` handler:
        ```python
        async def credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            user_t极g = update.effective_user
            db: Session = SessionLocal()
            try:
                user_db = user_service.get_user_by_telegram_id(db,