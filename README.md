

# AI-Powered Development Assistant Bot

This repository contains the source code for an autonomous AI software development assistant. The bot, accessible via Telegram, takes user requirements and iteratively builds, verifies, and delivers complete software projects. It leverages a sophisticated agent-based architecture, a credit-based monetization system, and is built to be deployed in a containerized environment.

## ✨ Features

-   **Conversational Requirement Gathering:** Engages users to understand project needs.
-   **AI-Powered Planning:** An "Architect" agent generates technical plans, technology stacks, and detailed TODO lists.
-   **Iterative Implementation:** "Implementer" agents write code to complete tasks from the TODO list.
-   **Aider Integration:** Capable of in-place code refinement and editing.
-   **Automated Verification:** The Architect agent reviews implemented code against project goals.
-   **Credit-Based System:** Users operate on a credit balance, with costs deducted for LLM usage.
-   **Project Delivery:** Completed projects, including a generated `README.md`, are delivered as a ZIP file.
-   **Production-Ready:** Built with FastAPI, SQLAlchemy, Alembic for migrations, and includes Docker/Kubernetes configurations.

## ⚙️ Technology Stack

-   **Backend:** Python 3.11+, FastAPI
-   **AI Agents:** Google Gemini & OpenRouter models
-   **Database:** PostgreSQL
-   **Cache/Queue:** Redis
-   **Database Migrations:** Alembic
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

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/ai-dev-bot-platform.git
cd ai-dev-bot-platform
```

### 3. Configure Your Environment

This is the most crucial step. You need to create a `.env` file to store your secrets and configuration.

1.  Copy the example file:
    ```bash
    cp .env.example .env
    ```
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

### 4. Start Backend Services

Use Docker Compose to start the PostgreSQL database and Redis in the background.

```bash
docker-compose up -d postgres redis
```
This command starts only the services the application depends on, leaving the application itself to be run directly for easier debugging.

### 5. Set Up the Python Environment

1.  Create and activate a virtual environment:

    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

2.  Install all the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

### 6. Run Database Migrations

With the database running in Docker and your environment configured, apply the latest database schema using Alembic.

```bash
alembic upgrade head
```
This command reads your models, compares them to the database, and creates/updates tables as needed. You only need to run this once initially, and then again anytime the database models change.

### 7. Run the Application

Now, you can start the main application. This single command will launch the FastAPI server, which in turn starts the Telegram bot polling in the background.

```bash
uvicorn ai_dev_bot_platform.main:app --reload
```
-   `--reload` enables hot-reloading, so the server will restart automatically when you save code changes.

### 8. Interact with Your Bot

Go to Telegram, find the bot you created with BotFather, and send the `/start` command. The application running in your terminal should log the interaction, and the bot should reply. You're all set!

### Running with a Proxy

If you are behind a corporate or local proxy, you can inject the proxy settings into the Docker containers.

1.  **Create a Proxy Environment File:** In the project root (`ai_dev_bot_platform`), create a file named `.env.proxy`.

2.  **Add Proxy Settings:** Add your proxy configuration to the `.env.proxy` file. The `NO_PROXY` variable is crucial to ensure containers can communicate with each other directly.
    ```env
    # .env.proxy
    HTTP_PROXY=http://your.proxy.server:port
    HTTPS_PROXY=http://your.proxy.server:port
    NO_PROXY=localhost,127.0.0.1,postgres,redis
    ```

3.  **Build and Run with Proxy:** From the **project root (`ai_dev_bot_platform`)**, run the following command. It loads your standard `.env` file and the new `.env.proxy` file into the correct `docker-compose.yml`.
    ```bash
    docker-compose --env-file .env --env-file .env.proxy -f deploy/docker/docker-compose.yml up -d --build
    ```
    This will start all services (app, postgres, redis) and correctly inject your proxy settings into the `app` container for both the build process and runtime.

4.  **Apply Migrations:** This step is similar. Run migrations using the same environment files:
    ```bash
    docker-compose --env-file .env --env-file .env.proxy -f deploy/docker/docker-compose.yml exec app alembic upgrade head
    ```
 
### Testing Stripe Webhooks Locally
 
To test the full payment flow with Stripe, you need a way for Stripe's servers to send events to your local machine. We use `ngrok` for this.
 
1.  **Install `ngrok`:** Follow the instructions on the [ngrok website](https://ngrok.com/download).
 
2.  **Run `ngrok`:** In a separate terminal, start `ngrok` to expose your local port 8000 to the internet.
    ```bash
    ngrok http 8000
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