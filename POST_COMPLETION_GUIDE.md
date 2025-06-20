# Project Completion Guide: Telegram-Darvin

Congratulations! The automated development process is complete. This guide provides the next steps for running, testing, and extending your new application.

## 1. First-Time Setup

1.  **Install Dependencies:**
    Based on the project structure, run the following command:
    `pip install -r requirements.txt`

2.  **Configure Environment Variables:**
    A `.env.example` file has been created. Copy it to a new `.env` file:
    `cp ai_dev_bot_platform/.env.example ai_dev_bot_platform/.env`

    Open the `ai_dev_bot_platform/.env` file and replace the placeholder values with your actual secrets and configuration. The required keys are:
    `TELEGRAM_BOT_TOKEN`
    `DATABASE_URL`
    `OPENAI_API_KEY`
    `STRIPE_API_KEY`

## 2. Running the Application

The project is set up to run with Docker Compose.

*   **To run with Docker:**
    `docker-compose -f ai_dev_bot_platform/docker-compose.yml up --build`

Once running, the Telegram bot will be active and ready to receive messages.

## 3. Next Steps: Generating a Test Suite

This project was built without a test suite to ensure a fast, autonomous build. You can now use an AI assistant to create one.

**Provide the following prompt to an LLM like Roo to create the tests:**

> "Analyze the attached codebase. Based on the file `pytest.ini`, the primary testing framework is Pytest. Please generate a comprehensive test suite that provides full coverage for all features outlined in `docs/canonical_spec.md`. Place the generated test files in the `tests/` directory."

## 4. Project Finalization
*   You **must** handoff to `<mode>dispatcher</mode>`.
*   After the successful handoff, you can use the `attempt_completion` tool to finalize the project lifecycle.