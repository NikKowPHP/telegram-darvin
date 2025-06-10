Of course. Here is a new, highly detailed `implementation_todo.md` file designed to be executed by a small, autonomous 4B LLM agent.

This plan breaks down the advanced orchestration, testing, and CI/CD setup into simple, sequential, and explicit steps. Each task is an atomic unit of work with clear verification criteria to ensure a successful and robust implementation.

---
Here is the content for the new file:

# `implementation_todo.md` - Production Polish and Automation

**Project Goal:** To implement advanced orchestration logic, expand the test suite for full coverage, and create a complete CI/CD pipeline for automated testing and deployment.

**Guiding Principle:** Complete each task in the exact order it is presented. Verify each step before proceeding to the next.

---

## Feature 1: Advanced Orchestration Logic

**Goal:** Make the bot's interaction flow more robust by handling insufficient credit scenarios and interactive feedback for rejected tasks.

*   `[x]` **F1.1: Add Pre-emptive Credit Check**
    *   **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
    *   **Action:** In the `_handle_implement_task` method, at the very beginning (before fetching the project), add this credit check block:
        ```python
        # Add a pre-emptive check for credits before starting a task
        if user.credit_balance < 1.0: # A reasonable minimum threshold
            return {
                'text': "Your credit balance is too low to start a new task. Please /credits to top up.",
                'zip_buffer': None
            }
        ```
    *   **Verification:** The `_handle_implement_task` method now checks for a minimum credit balance before executing.

*   `[x]` **F1.2: Improve Handling of Rejected Implementations**
    *   **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
    *   **Action:** Find the `_handle_implement_task` method. Locate the `elif verification_status == "REJECTED":` block. Replace the entire block with the following logic, which gives the user a clear, actionable next step.
        ```python
        elif verification_status == "REJECTED":
            # Do not mark TODO as complete. Provide clear instructions for refinement.
            self.project_service.update_project(self.db, project.id, ProjectUpdate(status="awaiting_refinement"))
            feedback_message = (
                f"Task '{todo_item}' was REJECTED by the Architect.\n\n"
                f"**Feedback:**\n{verification_feedback}\n\n"
                "To fix this, you can use the `refine` command. Example:\n"
                f"`refine file {implementation.get('filename', 'path/to/your/file.py')} in project {project.id} with instruction: [Your instructions to fix the issue based on feedback]`"
            )
            return {'text': feedback_message, 'zip_buffer': None}
        ```
    *   **Verification:** The logic for a `REJECTED` verification now returns a detailed message guiding the user on how to use the `refine` command.

---

## Feature 2: Comprehensive Test Suite Expansion

**Goal:** Increase test coverage to include the new payment and Aider/refinement flows.

*   `[x]` **F2.1: Create a Test for the Payment Service**
    *   **File:** `ai_dev_bot_platform/tests/test_services.py`
    *   **Action:** Add the following new test function to the end of the file. This test will use `mocker` to simulate the Stripe API call.
        ```python
        from app.services.payment_service import PaymentService

        def test_create_checkout_session(mocker):
            # 1. Setup
            mock_stripe_session = mocker.patch('stripe.checkout.Session.create')
            mock_stripe_session.return_value = {"url": "https://fake.stripe.url/session123"}
            
            payment_service = PaymentService()
            # This user object is simplified for testing purposes
            mock_user = User(id=1, telegram_user_id=12345)
            
            # 2. Action
            result_url = payment_service.create_checkout_session(user=mock_user, credit_package='buy_100')
            
            # 3. Assert
            assert result_url == "https://fake.stripe.url/session123"
            mock_stripe_session.assert_called_once()
            # Verify that our internal user ID was passed to Stripe
            assert mock_stripe_session.call_args[1]['client_reference_id'] == '1'
        ```
    *   **Verification:** The file `test_services.py` now contains a test for `PaymentService`.

*   `[x]` **F2.2: Create a Test for the Aider Refinement Flow**
    *   **File:** `ai_dev_bot_platform/tests/test_orchestrator.py`
    *   **Action:** Add the following new test function to the file. This test verifies the stateless file handling logic.
        ```python
        @pytest.mark.asyncio
        async def test_handle_refine_request_flow(mocker):
            # 1. Setup
            mock_db = MagicMock()
            
            # Mock services
            mocker.patch('app.services.orchestrator_service.APIKeyManager')
            mocker.patch('app.services.orchestrator_service.LLMClient')
            mocker.patch('app.services.orchestrator_service.ArchitectAgent')
            mock_implementer_agent = mocker.patch('app.services.orchestrator_service.ImplementerAgent')
            mock_project_service = mocker.patch('app.services.orchestrator_service.ProjectService')
            mock_file_service = mocker.patch('app.services.orchestrator_service.ProjectFileService')
            mock_storage_service = mocker.patch('app.services.orchestrator_service.StorageService')

            # Instantiate the orchestrator
            orchestrator = ModelOrchestrator(mock_db)
            
            # Configure mocks
            fake_project_id = uuid.uuid4()
            mock_project_service.return_value.get_project.return_value = MagicMock(id=fake_project_id)
            mock_storage_service.return_value.download_file.return_value = "original code"
            mock_implementer_agent.return_value.apply_changes_with_aider = AsyncMock(
                return_value={"status": "success"}
            )

            # 2. Action
            test_user = User(id=1, telegram_user_id=123, credit_balance=100, created_at=None, updated_at=None)
            await orchestrator._handle_refine_request(test_user, str(fake_project_id), "src/main.py", "add a comment")
            
            # 3. Assert
            mock_storage_service.return_value.download_file.assert_called_once_with(str(fake_project_id), "src/main.py")
            mock_implementer_agent.return_value.apply_changes_with_aider.assert_awaited_once()
            mock_storage_service.return_value.upload_file.assert_called_once()
            mock_file_service.return_value.update_file_content.assert_called_once()
        ```
    *   **Verification:** The new test `test_handle_refine_request_flow` exists in `test_orchestrator.py` and correctly mocks the required services.

---

## Feature 3: CI/CD Automation Pipeline

**Goal:** Create a GitHub Actions workflow to automatically test the code on every push and pull request.

*   `[x]` **F3.1: Create the Continuous Integration (CI) Workflow File**
    *   **File:** `.github/workflows/ci.yml` (Create the `.github` and `workflows` directories in the project root)
    *   **Action:** Add the following content to the new file.
        ```yaml
        name: Build and Test

        on:
          push:
            branches: [ "main" ]
          pull_request:
            branches: [ "main" ]

        jobs:
          build-and-test:
            runs-on: ubuntu-latest
            
            steps:
            - name: Checkout repository
              uses: actions/checkout@v4

            - name: Set up Python 3.11
              uses: actions/setup-python@v5
              with:
                python-version: '3.11'

            - name: Install dependencies
              run: |
                python -m pip install --upgrade pip
                pip install -r ai_dev_bot_platform/requirements.txt

            - name: Run tests with pytest
              run: |
                # The root of the project is the checkout directory, 
                # so we run pytest from there.
                pytest ai_dev_bot_platform/tests/
        ```
    *   **Verification:** The file `.github/workflows/ci.yml` exists and contains the correct YAML configuration for a CI pipeline. When pushed to GitHub, this action will automatically run.