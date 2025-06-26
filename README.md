

# AI-Powered Development Assistant Bot

This repository contains the source code for an autonomous AI software development assistant. The bot, accessible via Telegram, takes user requirements and iteratively builds, verifies, and delivers complete software projects. It leverages a sophisticated agent-based architecture, a credit-based monetization system, and is built to be deployed in a containerized environment.

## ✨ Features

-   **Conversational Requirement Gathering:** Engages users to understand project needs.
-   **AI-Powered Planning:** An "Architect" agent generates technical plans, technology stacks, and detailed TODO lists.
-   **Iterative Implementation:** "Implementer" agents write code to complete tasks from the TODO list.
-   **Aider Integration:** Capable of in-place code refinement and editing.
-   **Automated Verification:** The Architect agent reviews implemented code against project goals.
-   **Codebase Indexing:** Fast semantic search across project code using AST analysis and FAISS indexing.

### Automated Verification Details
The system includes a comprehensive verification system that ensures code quality and adherence to requirements:

- **VerificationService**: Core service that performs syntax checks, architecture validation, and requirement compliance verification.
- **API Endpoints**:
  - `POST /api/v1/verify` - Main endpoint for code verification
  - Returns JSON with validation status, issues list, and detailed report
- **Integration**: Seamlessly works with the Architect agent to validate implementations
-   **Credit-Based System:** Users operate on a credit balance, with costs deducted for LLM usage.
-   **Conversation Logging:** All user interactions are stored in the database for quality assurance and continuous improvement.
-   **Project Delivery:** Completed projects, including a generated `README.md`, are delivered as a ZIP file.
-   **Production-Ready:** Built with FastAPI, SQLAlchemy, Alembic for migrations, and includes Docker/Kubernetes configurations.

## 💬 Conversation Logging

The system automatically logs all user interactions with the following details:
- User ID
- Timestamp
- Full message history
- Project context (when available)

This helps with:
- Debugging user issues
- Improving AI responses through analysis
- Maintaining audit trails

### Example Usage
```python
from app.services.conversation_service import ConversationService
from app.db.session import SessionLocal

db = SessionLocal()
conversation_service = ConversationService(db)

# Get last 10 conversations for a user
recent_convs = conversation_service.get_conversations_by_user(
    user_id=123,
    limit=10
)

# Get conversations containing specific keywords
search_results = conversation_service.search_conversations(
    search_text="API error"
)
```

## ⚙️ Technology Stack

-   **Backend:** Python 3.11+, FastAPI
-   **AI Agents:** Google Gemini & OpenRouter models
-   **Database:** PostgreSQL
-   **Cache/Queue:** Redis
-   **Database Migrations:** Alembic

### Codebase Indexing Details
The system includes a powerful code search capability that understands code structure:

- **AST-based Vectorization:** Converts code to vectors based on abstract syntax tree node frequencies
- **FAISS Indexing:** Efficient similarity search using Facebook's FAISS library
- **Real-time Updates:** Index stays in sync with code changes

Example usage:
```python
from app.services.codebase_indexing_service import CodebaseIndexingService

indexer = CodebaseIndexingService()
indexer.index_codebase([
    {'path': 'src/main.py', 'content': 'def main(): print("Hello")'},
    {'path': 'src/utils.py', 'content': 'def helper(): return 42'}
])

results = indexer.search_codebase('print', k=1)
print(results[0]['file'])  # Output: src/main.py
```
-   **Telegram Integration:** `python-telegram-bot`
-   **Containerization:** Docker, Docker Compose
-   **Deployment:** Kubernetes

---

## 🚀 Running Locally

This guide will walk you through setting up and running the entire application on your local machine for development.

### 1. Prerequisites

Before you begin, ensure you have the following installed:
-   **Git:** To clone the repository.
-   **Python 3.11+:** To run the application.
-   **Docker & Docker Compose:** To run the database (PostgreSQL) and cache (Redis).
-   **Telegram Bot Token:** Get one from the [BotFather](https://t.me/BotFather) on Telegram.
-   **LLM API Keys:**
    -   A **Google Gemini API Key**.
    -   An **OpenRouter API Key**.



### 3. Configure Your Environment

This is the most crucial step. You need to create a `.env` file to store your secrets and configuration.

1.  Copy the example file:



    cp .env.example .env
 


2.  Open the new `.env` file in your editor and fill in the required values:

    ```env

    # Application
    APP_ENV="development"
    LOG_LEVEL="INFO"

    # Database (PostgreSQL) - You can leave these as is for local Docker setup
    POSTGRES_USER="your_db_user"
    POSTGRES_PASSWORD="your_db_password"
    POSTGRES_SERVER="localhost"
    POSTGRES_PORT="5432"
    POSTGRES_DB="ai_dev_bot"

    # Telegram - PASTE YOUR TOKEN HERE
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"

    # LLM API Keys - PASTE YOUR KEYS HERE
    GOOGLE_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
    OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY"

    # Stripe (can be left as placeholders for now)
    STRIPE_SECRET_KEY="sk_test_YOUR_KEY"
    STRIPE_WEBHOOK_SECRET="whsec_YOUR_KEY"


    ```


This command starts only the services the application depends on, leaving the application itself to be run directly for easier debugging.

### 5. Set Up the Python Environment

1.  Create and activate a virtual environment:

    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows (using py command)
    py -m venv venv
    .\venv\Scripts\activate
    ```

    Alternatively, use the Windows batch script:
    ```batch
    setup_venv.bat
    ```

2.  Install all the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

### 6. Test Environment Setup

The test environment requires a virtual environment to be set up. The `run_tests.sh` script will automatically create the virtual environment if it doesn't exist:

1.  To run the tests, simply execute:

    ```bash
    bash run_tests.sh
    ```

    On Windows, you can also use the batch script:
    ```batch
    setup_venv.bat
    pytest
    ```

2.  The script will:
    - Check if the virtual environment exists
    - Create it if missing
    - Activate the virtual environment
    - Install any missing dependencies from `requirements.txt`
    - Run the test suite using `pytest`
    - Generate an audit report using `allure`

This ensures a consistent test environment across different development setups.

### 7. Run Database Migrations

With the database running in Docker and your environment configured, apply the latest database schema using Alembic.

alembic upgrade head

`cd ai_dev_bot_platform && /home/kasjer/projects/telegram-darvin/ai_dev_bot_platform/venv/bin/alembic upgrade head`.




### 7. Run the Application

Now, you can start the main application. This single command will launch the FastAPI server, which in turn starts the Telegram bot polling in the background.


docker-compose exec app uvicorn main:app --reload


-   `--reload` enables hot-reloading, so the server will restart automatically when you save code changes.

### 8. Interact with Your Bot

Go to Telegram, find the bot you created with BotFather, and send the `/start` command. The application running in your terminal should log the interaction, and the bot should reply. You're all set!

### 9. Running the Autonomous Loop

To start the development workflow:
```bash
python run_autonomy.py
```

The system will continuously run the Orchestrator agent to manage development tasks.

### 10. Installing Roo CLI Dependencies

The autonomous loop requires the Roo CLI to be installed. If you encounter errors about the `roo` command not being found, follow these steps:

1. **Install Roo CLI**:
   ```bash
   cd ai_dev_bot_platform
   pip install -r requirements.txt
   ```

2. **Verify Installation**:
   ```bash
   ./venv/bin/roo -h
   ```

If you still encounter issues, ensure that the virtual environment is activated and that the `roo` command is accessible from the project root.

### Testing Stripe Webhooks Locally
 
To test the full payment flow with Stripe, you need a way for Stripe's servers to send events to your local machine. We use `ngrok` for this.
 
1.  **Install `ngrok`:** Follow the instructions on the [ngrok website](https://ngrok.com/download).
 
2.  **Run `ngrok`:** In a separate terminal, start `ngrok` to expose your local port 8345 to the internet.
    ```bash
    ngrok http 8345
    ```
 
3.  **Get Your Webhook URL:** `ngrok` will give you a public URL (e.g., `https://random-string.ngrok.io`). Your full webhook URL will be this URL plus the API path:
    `https://random-string.ngrok.io/api/v1/stripe-webhook`
 
4.  **Configure Stripe:** Go to your Stripe Dashboard, navigate to the "Webhooks" section, and add a new endpoint. Paste the full URL from the previous step. For the events, select "Listen to all events" for now, or specifically `checkout.session.completed`.
 
5.  **Set `MOCK_STRIPE_PAYMENTS` to `false`** in your `.env` file to enable the live Stripe flow. Now, when you click a "Buy Credits" button, you will be redirected to a real Stripe checkout page. After a successful payment, Stripe will send an event to your `ngrok` URL, which will forward it to your local application to grant the credits.
 
---
 
## 🌐 Deployment (Cloud Run & Supabase)

This section provides a complete guide for deploying the application to a scalable, serverless environment using Google Cloud Run for the application and Supabase for the database and file storage.

### 1. Supabase Setup

Before deploying the application, you need to set up your Supabase project.

1.  **Create a Project:** Go to [supabase.com](https://supabase.com) and create a new project.
2.  **Get Database URL:** In your project's dashboard, go to `Settings` > `Database`. Find your connection string (URI) and use its components for the `POSTGRES_*` variables in your `.env` file.
3.  **Get API Keys:** Go to `Settings` > `API`. You will find your `SUPABASE_URL` (Project URL) and `SUPABASE_KEY` (the `service_role` key).
4.  **Create a Storage Bucket:** Go to `Storage` and create a new public bucket for each project you intend to test. The bucket name should be the Project ID (a UUID). For simplicity during testing, you can create one bucket with a known UUID and use that for your test project.

### 2. Configure Environment for Production

Create a `.env` file in your project root and fill it with your **production** keys from Supabase, Telegram, and your LLM providers. Ensure `MOCK_STRIPE_PAYMENTS` is set to `false`.

### 3. Build and Push the Docker Image

The application will run as a container on Cloud Run.

1.  **Enable Google Cloud Services:** Make sure you have enabled the Artifact Registry API and the Cloud Run API in your Google Cloud project.
2.  **Authenticate Docker:** Configure Docker to authenticate with Google Cloud's Artifact Registry.
    ```bash
    gcloud auth configure-docker your-region-docker.pkg.dev
    ```
    *(Replace `your-region` with your GCP region, e.g., `us-central1`)*

3.  **Build the Image:** From the project root (`ai_dev_bot_platform`), build the Docker image.
    ```bash
    docker build -t your-region-docker.pkg.dev/your-gcp-project-id/ai-dev-bot:latest -f deploy/docker/Dockerfile .
    ```

4.  **Push the Image:**
    ```bash
    docker push your-region-docker.pkg.dev/your-gcp-project-id/ai-dev-bot:latest
    ```

### 4. Deploy to Google Cloud Run

Deploy the container image using the `gcloud` command-line tool. This single command sets up the service, injects all secrets as environment variables, and exposes it to the internet.

```bash
gcloud run deploy ai-dev-bot-service \
  --image your-region-docker.pkg.dev/your-gcp-project-id/ai-dev-bot:latest \
  --platform managed \
  --region your-gcp-region \
  --allow-unauthenticated \
  --set-env-vars="POSTGRES_USER=your_db_user" \
  --set-env-vars="POSTGRES_PASSWORD=your_db_password" \
  --set-env-vars="POSTGRES_SERVER=db.your-project-id.supabase.co" \
  --set-env-vars="POSTGRES_PORT=5432" \
  --set-env-vars="POSTGRES_DB=postgres" \
  --set-env-vars="TELEGRAM_BOT_TOKEN=your_telegram_token" \
  --set-env-vars="GOOGLE_API_KEY=your_google_key" \
  --set-env-vars="OPENROUTER_API_KEY=your_openrouter_key" \
  --set-env-vars="API_KEY_ENCRYPTION_KEY=a_strong_random_secret" \
  --set-env-vars="SUPABASE_URL=https://your-project-id.supabase.co" \
  --set-env-vars="SUPABASE_KEY=your_supabase_service_role_key" \
  --set-env-vars="STRIPE_SECRET_KEY=sk_live_your_key" \
  --set-env-vars="STRIPE_WEBHOOK_SECRET=whsec_your_key" \
  --set-env-vars="MOCK_STRIPE_PAYMENTS=false"
```
-   **Note:** After deployment, Cloud Run will provide a public URL for your service. Use this URL to configure your Stripe webhook endpoint.

### 5. Run Database Migrations

The recommended way to run migrations on Cloud Run is to submit a one-off Cloud Build job that uses the same container image.

1.  Create a `cloudbuild.yaml` file in your project root:
    ```yaml
    steps:
    - name: 'your-region-docker.pkg.dev/your-gcp-project-id/ai-dev-bot:latest'
      entrypoint: 'alembic'
      args: ['upgrade', 'head']
      secretEnv: ['POSTGRES_USER', 'POSTGRES_PASSWORD']
    
    availableSecrets:
      secretManager:
      - versionName: projects/your-gcp-project-id/secrets/POSTGRES_USER/versions/latest
        env: 'POSTGRES_USER'
      - versionName: projects/your-gcp-project-id/secrets/POSTGRES_PASSWORD/versions/latest
        env: 'POSTGRES_PASSWORD'
    ```
    *(This requires you to store your DB credentials in Google Secret Manager first.)*

2.  Submit the build:
    ```bash
    gcloud builds submit --config cloudbuild.yaml .
    ```