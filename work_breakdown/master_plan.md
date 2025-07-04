# AI Developer Work Plan: Audit Remediation

This work plan translates the findings of the project audit into a set of prioritized, atomic tasks for an AI developer agent. The objective is to resolve all identified discrepancies and bring the codebase into full alignment with its documentation and best practices.

---

## P0 - Critical Code Fixes & Refactoring

This tier addresses the most severe structural and security issues identified in the audit. Completing these tasks is a prerequisite for all other work.

- [x] **REFACTOR**: Consolidate the `VerificationService` into the main application structure.
    - **File**: `ai_dev_bot_platform/app/services/verification_service.py`
    - **Action**: Move the content from the extraneous `app/services/verification_service.py` into this file, replacing its current placeholder content. Ensure all dependencies are correctly imported within the `ai_dev_bot_platform` scope.
    - **Reason**: Audit finding: Feature Completeness. The `VerificationService` is not properly integrated into the main `ai_dev_bot_platform` application.

- [x] **REFACTOR**: Delete the redundant top-level `app` directory to eliminate code duplication.
    - **File**: `app/` (the entire directory at the root)
    - **Action**: After consolidating necessary files in the previous step, delete the entire top-level `app` directory and all its contents.
    - **Reason**: Audit finding: Undocumented Functionality. The presence of two `app` directories is a critical structural flaw causing massive confusion and code duplication.

- [x] **FIX**: Secure the administrative credit-setting endpoint.
    - **File**: `ai_dev_bot_platform/main.py`
    - **Action**: Modify the `set_user_credits` endpoint. Add a new dependency that checks for a secret header (e.g., `X-Admin-Token`). The endpoint should only proceed if the token in the header matches a new, hardcoded secret string.
    - **Reason**: Audit finding: Undocumented Functionality. The endpoint `POST /admin/set-credits/{telegram_user_id}` is unauthenticated, posing a major security risk.

- [x] **REFACTOR**: Internalize the "Autonomous Loop" logic.
    - **File**: `ai_dev_bot_platform/app/services/orchestrator_service.py`
    - **Action**: Implement a new public async method named `run_autonomous_loop` within the `OrchestratorService` class. This method will contain the core logic from the `run_autonomy.py` script (finding the next task from a markdown file, executing it, and updating its status). This method should not depend on the external `roo` CLI.
    - **Reason**: Audit finding: Feature Completeness. The "Autonomous Loop" is currently handled by an undocumented external script (`run_autonomy.py`) with a missing dependency, making it non-functional and unauditable.

---

## P1 - Implementation of Missing Features

This tier adds the necessary API endpoints and integrations for features that were refactored in P0.

- [x] **CREATE**: Implement the API endpoint for the `VerificationService`.
    - **File**: `ai_dev_bot_platform/app/api/endpoints/verification.py` (Create this new file)
    - **Action**: Create a new FastAPI router in this file. Add a `POST /verify` endpoint that accepts a code snippet and project context, calls the `architect_agent.verify_implementation_step` method, and returns the verification result.
    - **Reason**: Audit finding: API/Function Discrepancies. The verification feature was not exposed via an API endpoint in the main application.

- [x] **CREATE**: Implement the API endpoint to trigger the autonomous loop.
    - **File**: `ai_dev_bot_platform/app/api/endpoints/orchestrator.py`
    - **Action**: Add a new `POST /orchestrate/run-loop` endpoint to the existing router. This endpoint should call the `run_autonomous_loop` method on the `OrchestratorService`.
    - **Reason**: Audit finding: Feature Completeness. The trigger for the "Autonomous Loop" was external and non-functional. This brings control of the loop inside the application.

---

## P2 - Correcting Mismatches

This tier is empty as the major mismatches were structural and resolved by the P0 refactoring (deleting the duplicate `app` directory).

---

## P3 - Documentation Updates

This tier ensures that all configurations, endpoints, and scripts are properly documented.

- [x] **DOCS**: Update `.env.example` with missing Redis and LLM model variables.
    - **File**: `ai_dev_bot_platform/.env.example`
    - **Action**: Add the following environment variables to the file with placeholder values: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`, `ARCHITECT_MODEL`, `IMPLEMENTER_MODEL`, `VERIFICATION_MODEL`, `DEFAULT_GEMINI_MODEL`.
    - **Reason**: Audit finding: Configuration Mismatches. Critical variables for Redis and LLM models were used in the code but not documented.

- [x] **DOCS**: Update `.env.example` with missing Stripe and Supabase variables.
    - **File**: `ai_dev_bot_platform/.env.example`
    - **Action**: Add the following environment variables to the file with placeholder values: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`, `MOCK_STRIPE_PAYMENTS`, `SUPABASE_URL`, `SUPABASE_KEY`, `WEBAPP_URL`.
    - **Reason**: Audit finding: Configuration Mismatches. Critical variables for payment processing and file storage were used in the code but not documented.

- [x] **DOCS**: Document the newly secured admin credit endpoint.
    - **File**: `documentation/srs.md`
    - **Action**: Add a new section under "Functional Requirements" for the `POST /admin/set-credits` endpoint, clearly stating its purpose and that it requires an `X-Admin-Token` header for authentication.
    - **Reason**: Audit finding: Undocumented Functionality. The admin endpoint needs to be documented for operational awareness.

- [ ] **DOCS**: Document the application health check endpoints.
    - **File**: `documentation/operations_manual.md`
    - **Action**: Add a subsection under "Monitoring" that lists the available health endpoints (`/health`, `/ready`, `/telegram`, `/metrics`) and their purpose.
    - **Reason**: Audit finding: Undocumented Functionality. The health endpoints are crucial for operations but were not documented.

- [ ] **DOCS**: Document the utility scripts `cli_runner.py` and `seed_db.py`.
    - **File**: `documentation/operations_manual.md`
    - **Action**: Add a new section titled "Utility Scripts" describing the purpose and basic usage of `cli_runner.py` and `seed_db.py`.
    - **Reason**: Audit finding: Undocumented Functionality. The utility scripts were not documented.

- [ ] **DOCS**: Update the architecture map to reflect the consolidated code structure.
    - **File**: `docs/architecture_map.md`
    - **Action**: Review all file paths in the architecture map. Remove any references to files that were in the deleted top-level `app` directory and ensure all paths point to their new locations within `ai_dev_bot_platform/app/`.
    - **Reason**: Audit finding: The codebase structure was changed, and documentation must now reflect the single source of truth.