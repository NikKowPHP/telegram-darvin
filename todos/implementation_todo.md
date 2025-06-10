Of course. Here is a new, highly detailed `implementation_todo.md` file designed to fix the inconsistencies with the Supabase integration.

The plan is structured with extreme simplicity and clarity, breaking down the refactoring into atomic, verifiable steps suitable for a small 4B LLM agent.

---
Here is the content for the new file:

# `implementation_todo.md` - Supabase Integration and Final Fixes

**Project Goal:** To fully integrate Supabase Storage into the application's core workflows, ensuring that all file operations are stateless and ready for a serverless environment. This includes automating storage bucket creation, fixing the file implementation and delivery flows, and updating the test suite.

**Guiding Principle:** Complete each task in the exact order it is presented. Verify each step before proceeding to the next.

---

## Feature 1: Automate Supabase Bucket Creation

**Goal:** Ensure that a dedicated storage bucket is automatically created in Supabase for every new project.

*   `[x]` **F1.1: Add a `create_bucket` method to the Storage Service**
    *   **File:** `ai_dev_bot_platform/app/services/storage_service.py`
    *   **Action:** Add the following new method to the `StorageService` class.
        ```python
        def create_bucket(self, bucket_name: str) -> bool:
            if not self.client:
                logger.error("Storage client not initialized. Cannot create bucket.")
                return False
            try:
                self.client.storage.create_bucket(bucket_name)
                logger.info(f"Successfully created bucket: {bucket_name}")
                return True
            except Exception as e:
                # APIError: 'Bucket already exists' is a common, non-fatal error here.
                if "Bucket already exists" in str(e):
                    logger.warning(f"Bucket '{bucket_name}' already exists. Skipping creation.")
                    return True
                logger.error(f"Failed to create bucket {bucket_name}: {e}", exc_info=True)
                return False
        ```
    *   **Verification:** The `StorageService` class now has a `create_bucket` method.

*   `[ ]` **F1.2: Call `create_bucket` when a new project is handled**
    *   **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
    *   **Action:** In the `_handle_new_project` method, immediately after the `project = self.project_service.create_project(...)` line, insert the following code block:
        ```python
        # Create a dedicated storage bucket for this project
        self.storage_service.create_bucket(str(project.id))
        ```
    *   **Verification:** The orchestrator now attempts to create a Supabase bucket every time a new project is created.

---

## Feature 2: Fix File Implementation and Delivery Flows

**Goal:** Refactor the implementer and delivery flows to use Supabase Storage as the single source of truth for file content.

*   `[ ]` **F2.1: Upload newly implemented files to Supabase Storage**
    *   **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
    *   **Action:** In the `_handle_implement_task` method, locate the block that starts with `if implementation["filename"] and implementation["code"]:`. Inside this block, after the call to `self.project_file_service.create_project_file(...)`, add the following code:
        ```python
        # Also upload the new file to Supabase Storage
        self.storage_service.upload_file(
            bucket_name=str(project.id),
            file_path=implementation["filename"],
            file_content=implementation["code"]
        )
        ```
    *   **Verification:** When the implementer agent creates a new file, it is now saved to the database AND uploaded to the project's Supabase bucket.

*   `[ ]` **F2.2: Add a `list_files` method to the Storage Service**
    *   **File:** `ai_dev_bot_platform/app/services/storage_service.py`
    *   **Action:** Add the following new method to the `StorageService` class. This is needed to get all file names before creating the ZIP.
        ```python
        def list_files(self, bucket_name: str) -> list[dict]:
            if not self.client:
                logger.error("Storage client not initialized. Cannot list files.")
                return []
            try:
                return self.client.storage.from_(bucket_name).list()
            except Exception as e:
                logger.error(f"Failed to list files for bucket {bucket_name}: {e}", exc_info=True)
                return []
        ```
    *   **Verification:** The `StorageService` class now has a `list_files` method.

*   `[ ]` **F2.3: Refactor ZIP delivery to use files from Supabase Storage**
    *   **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
    *   **Action:** Find the `_handle_implement_task` method. Locate the section where the project status becomes `"verification_complete"`. Replace the two lines that fetch files from the database with logic that fetches them from storage.
        *   **Find and delete these two lines:**
            ```python
            # Fetch all project files
            db_project_files = self.project_file_service.get_project_files_by_project(self.db, project_id=project.id)
            project_files_for_readme = [{"file_path": pf.file_path, "content": pf.content} for pf in db_project_files]
            ```
        *   **In their place, insert this new logic:**
            ```python
            # Fetch all project files from Supabase Storage
            bucket_name = str(project.id)
            storage_files = self.storage_service.list_files(bucket_name)
            project_files_for_readme = []
            for storage_file in storage_files:
                file_content = self.storage_service.download_file(bucket_name, storage_file['name'])
                if file_content is not None:
                    project_files_for_readme.append({"file_path": storage_file['name'], "content": file_content})
            ```
    *   **Verification:** The project completion logic now builds the ZIP file using content downloaded directly from Supabase Storage, ensuring it is the true source of data.

---

## Feature 3: Update Test Suite for New Architecture

**Goal:** Modify the existing tests to account for the new `StorageService` and its role in the application's workflows.

*   `[ ]` **F3.1: Update the Orchestrator test to mock the Storage Service**
    *   **File:** `ai_dev_bot_platform/tests/test_orchestrator.py`
    *   **Action:** In the `test_handle_new_project_flow` test function, find the line `mock_project_service = mocker.patch(...)`. Directly after it, add a new line to mock the `StorageService`.
        ```python
        mock_storage_service = mocker.patch('app.services.orchestrator_service.StorageService')
        ```
    *   **Verification:** The `test_handle_new_project_flow` test now mocks the `StorageService`.

*   `[ ]` **F3.2: Add assertion for bucket creation in the Orchestrator test**
    *   **File:** `ai_dev_bot_platform/tests/test_orchestrator.py`
    *   **Action:** In the `test_handle_new_project_flow` test function, find the "Assert" section. Add the following line to verify that the bucket creation method is called.
        ```python
        # In the Assert section
        mock_storage_service.return_value.create_bucket.assert_called_once()
        ```
    *   **Verification:** The test now correctly asserts that the orchestrator tries to create a Supabase bucket for every new project.

