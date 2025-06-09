

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

---

## 🌐 Deployment

This section provides step-by-step instructions for deploying the application to a production-like environment.

### Method 1: Using Docker Compose (for Single-Server Deployments)

This is a simpler method suitable for a single virtual machine.

1.  **Configure `.env`:** Copy `.env.example` to `.env` on your server and fill it with your **production** keys and database credentials. Ensure `POSTGRES_SERVER` is set to `postgres` (the service name in `docker-compose.yml`).

2.  **Build and Run:** From the project root on your server, run the following command:
    ```bash
    docker-compose up -d --build
    ```
    -   `--build` forces Docker to rebuild your application image with the latest code.
    -   `-d` runs all services (app, postgres, redis) in the background.

3.  **Apply Migrations:** Run the Alembic migrations inside the running `app` container:
    ```bash
    docker-compose exec app alembic upgrade head
    ```

4.  **Managing the Deployment:**
    -   To view logs: `docker-compose logs -f app`
    -   To stop the services: `docker-compose down`

### Method 2: Using Kubernetes (for Production-Scale Deployments)

This is the recommended method for a scalable and resilient production environment.

#### 1. Prerequisites
- A running Kubernetes cluster (e.g., GKE, EKS, AKS, or a local one like Minikube).
- `kubectl` command-line tool configured to connect to your cluster.
- A Docker image registry (e.g., Docker Hub, Google Container Registry, Amazon ECR) that your Kubernetes cluster can access.

#### 2. Build and Push the Docker Image

1.  Build the application's Docker image, tagging it for your registry:
    ```bash
    docker build -t your-registry/ai-dev-bot-app:latest .
    ```
    *(Replace `your-registry` with your registry's path, e.g., `gcr.io/my-gcp-project`)*

2.  Push the image to your registry:
    ```bash
    docker push your-registry/ai-dev-bot-app:latest
    ```

#### 3. Update the Kubernetes Deployment Manifest

Edit `deploy/kubernetes/app-k8s.yaml` and change the placeholder image name to the one you just pushed.

```yaml
# in deploy/kubernetes/app-k8s.yaml
...
spec:
  containers:
  - name: ai-dev-bot-app
    image: your-registry/ai-dev-bot-app:latest # <-- UPDATE THIS LINE
...
```

#### 4. Create Kubernetes Secrets & ConfigMaps

You must create Kubernetes secrets to securely store your credentials. **Do not commit these files to Git.**

1.  **Create `postgres-secret.yaml`:**
    ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: postgres-secret
    type: Opaque
    data:
      user: $(echo -n 'your_db_user' | base64)
      password: $(echo -n 'your_db_password' | base64)
    ```

2.  **Create `app-secrets.yaml`:**
    ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: app-secrets
    type: Opaque
    data:
      TELEGRAM_BOT_TOKEN: $(echo -n 'YOUR_TELEGRAM_BOT_TOKEN' | base64)
      GOOGLE_API_KEY: $(echo -n 'YOUR_GOOGLE_GEMINI_API_KEY' | base64)
      OPENROUTER_API_KEY: $(echo -n 'YOUR_OPENROUTER_API_KEY' | base64)
      # ... and other secrets from .env
    ```

3.  **Apply the secrets and the existing ConfigMap:**
    ```bash
    kubectl apply -f postgres-secret.yaml
    kubectl apply -f app-secrets.yaml
    kubectl apply -f deploy/kubernetes/config-secrets-example.md # This contains the app-config ConfigMap
    ```

#### 5. Deploy the Services

Apply the Kubernetes manifest files to your cluster in order.

```bash
# Deploy PostgreSQL StatefulSet and Service
kubectl apply -f deploy/kubernetes/postgres-k8s.yaml

# Deploy Redis Deployment and Service
kubectl apply -f deploy/kubernetes/redis-k8s.yaml

# Deploy the Application itself
kubectl apply -f deploy/kubernetes/app-k8s.yaml
```

#### 6. Run Database Migrations (as a Job)

Create a one-off Kubernetes Job to run the Alembic migrations.

1.  Create `k8s-migration-job.yaml`:
    ```yaml
    apiVersion: batch/v1
    kind: Job
    metadata:
      name: alembic-migration
    spec:
      template:
        spec:
          containers:
          - name: alembic
            image: your-registry/ai-dev-bot-app:latest # Use the same app image
            command: ["alembic", "upgrade", "head"]
            envFrom:
              - configMapRef:
                  name: app-config
              - secretRef:
                  name: app-secrets
          restartPolicy: Never
      backoffLimit: 4
    ```

2.  Apply the job:
    ```bash
    kubectl apply -f k8s-migration-job.yaml
    ```

#### 7. Verify the Deployment

-   Check if all pods are in the `Running` state: `kubectl get pods`
-   Check the logs of your application pod: `kubectl logs -f <your-app-pod-name>`
-   Get the external IP address of your service (if using `type: LoadBalancer`): `kubectl get svc ai-dev-bot-app-service`

Your application is now deployed on Kubernetes