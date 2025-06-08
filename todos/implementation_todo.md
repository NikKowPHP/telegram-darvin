Okay, this is a significant task, and breaking it down for a 4B model requires extreme granularity and clear, sequential steps. The "prod condition" implies not just code but also basic configuration, environment variable handling, logging stubs, and Dockerization.

This `implementation_todo.md` will be very long. It will assume the 4B LLM is guided by a human or a more capable LLM to execute these steps, especially for reviewing, testing, and integrating complex parts. The 4B model will primarily focus on generating code snippets and file structures based on very specific instructions.

**Assumptions for the 4B LLM:**
1.  It can create files and write Python code based on detailed prompts.
2.  It understands basic project structures (directories, `__init__.py`).
3.  It can fill in simple configurations and placeholders.
4.  It will require human review and integration for complex logic or inter-service communication.
5.  It will create stubs/placeholders where full logic is too complex for one go.

Let's begin.

---

# `implementation_todo.md` - AI-Powered Development Assistant Bot

**Project Goal:** Implement the AI-Powered Development Assistant Telegram Bot platform, ready for initial production deployment.
**Primary Technologies:** Python, FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery, Docker, Kubernetes, `python-telegram-bot`, Google Gemini, OpenRouter.
**Source of Truth for Features & Architecture:** `documentation/high_level_documentation.md` and other supporting documents in `documentation/`.

---

## Phase 0: Foundation & Environment Setup

**Goal:** Establish the basic project structure, virtual environment, core dependencies, and initial configurations.

*   `[x]` **P0.1: Create Project Root Directory**
     *   Action: Create a root directory named `ai_dev_bot_platform`.
     *   Verification: Directory exists.

*   `[x]` **P0.2: Initialize Git Repository**
     *   Action: Inside `ai_dev_bot_platform`, run `git init`.
     *   Verification: `.git` directory created.

*   `[x]` **P0.3: Create Basic Directory Structure**
     *   Action: Inside `ai_dev_bot_platform`, create the following directories:
         *   `app/` (for all application code)
         *   `app/core/`
         *   `app/models/` (for SQLAlchemy models)
         *   `app/schemas/` (for Pydantic schemas)
         *   `app/services/`
         *   `app/api/` (for FastAPI endpoints)
         *   `app/telegram_bot/`
         *   `app/agents/`
         *   `app/utils/`
         *   `app/db/`
         *   `app/background_tasks/` (for Celery tasks)
         *   `config/` (for configuration files, though we'll primarily use env vars)
         *   `tests/`
         *   `scripts/` (for utility scripts)
         *   `deploy/` (for Dockerfiles, docker-compose, k8s manifests)
         *   `deploy/docker/`
         *   `deploy/kubernetes/`
     *   Verification: All directories exist.

*   `[x]` **P0.4: Create Initial Python Files**
     *   Action: Create `__init__.py` (can be empty) in:
         *   `app/`
         *   `app/core/`
         *   `app/models/`
         *   `app/schemas/`
         *   `app/services/`
         *   `app/api/`
         *   `app/telegram_bot/`
         *   `app/agents/`
         *   `app/utils/`
         *   `app/db/`
         *   `app/background_tasks/`
     *   File: `ai_dev_bot_platform/main.py` (entry point for FastAPI)
         *   Content:
             ```python
             from fastapi import FastAPI
             from app.core.logging_config import setup_logging

             app = FastAPI(title="AI Development Assistant API")

             setup_logging()

             @app.get("/")
             async def root():
                 return {"message": "AI Development Assistant API is running!"}

             # Placeholder for future app setup
             # def create_application() -> FastAPI:
             #     application = FastAPI()
             #     # ... add routers, middleware, etc.
             #     return application
             #
             # app = create_application()
             ```
     *   Verification: Files created.

*   `[x]` **P0.5: Setup `requirements.txt`**
     *   File: `ai_dev_bot_platform/requirements.txt`
     *   Content:
         ```
         fastapi
         uvicorn[standard]
         sqlalchemy
         psycopg2-binary # For PostgreSQL
         redis
         celery[redis]
         python-telegram-bot
         pydantic
         pydantic-settings
         httpx # For making API calls to LLMs
         google-generativeai # For Gemini
         # openrouter-client (if a specific client library is chosen, or use httpx)
         python-dotenv # For local .env file loading
         # Add other common utilities like 'requests' if needed later
         # For Codebase Indexing (add later when implementing that service)
         # sentence-transformers
         # faiss-cpu or other vector DB client
         ```
     *   Verification: File created.
     *   Note: Advise human to create a virtual environment (`python -m venv venv`) and install (`pip install -r requirements.txt`).

*   `[x]` **P0.6: Setup `.env.example` and Basic Configuration Loading**
     *   File: `ai_dev_bot_platform/.env.example`
         *   Content:
             ```env
             # Application
             APP_ENV="development" # development, staging, production
             LOG_LEVEL="INFO"

             # Database (PostgreSQL)
             POSTGRES_USER="your_db_user"
             POSTGRES_PASSWORD="your_db_password"
             POSTGRES_SERVER="localhost"
             POSTGRES_PORT="5432"
             POSTGRES_DB="ai_dev_bot"
             DATABASE_URL="postgresql://your_db_user:your_db_password@localhost:5432/ai_dev_bot"

             # Redis
             REDIS_HOST="localhost"
             REDIS_PORT="6379"
             REDIS_DB="0" # For Celery broker/backend and caching

             # Telegram
             TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"

             # LLM API Keys
             ## Google Gemini
             GOOGLE_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY" # Or path to service account json
             # GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google_service_account.json"

             ## OpenRouter
             OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY"

             # API Key Manager (Encryption for stored keys if any)
             API_KEY_ENCRYPTION_KEY="a_very_strong_random_secret_key_32_bytes"

             # Cost Management
             PLATFORM_CREDIT_VALUE_USD="0.01" # 1 credit = $0.01
             MARKUP_FACTOR="1.5" # 50% markup
             ```
     *   File: `ai_dev_bot_platform/app/core/config.py`
         *   Content:
             ```python
             from pydantic_settings import BaseSettings, SettingsConfigDict
             from typing import List, Dict, Any, Optional

             class Settings(BaseSettings):
                 APP_ENV: str = "development"
                 LOG_LEVEL: str = "INFO"

                 POSTGRES_USER: str
                 POSTGRES_PASSWORD: str
                 POSTGRES_SERVER: str
                 POSTGRES_PORT: str
                 POSTGRES_DB: str
                 DATABASE_URL: Optional[str] = None # Will be constructed if not provided

                 REDIS_HOST: str = "localhost"
                 REDIS_PORT: int = 6379
                 REDIS_DB: int = 0

                 TELEGRAM_BOT_TOKEN: str

                 GOOGLE_API_KEY: Optional[str] = None
                 GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
                 OPENROUTER_API_KEY: Optional[str] = None

                 API_KEY_ENCRYPTION_KEY: str # For encrypting any keys stored in DB (not external provider keys)

                 PLATFORM_CREDIT_VALUE_USD: float = 0.01
                 MARKUP_FACTOR: float = 1.5

                 # API Key Pools for round-robin (loaded from env or defaults)
                 # Example: GOOGLE_API_KEY_POOL='key1,key2'
                 # Example: OPENROUTER_API_KEY_POOL='keyA,keyB'
                 # These will be parsed into lists by the APIKeyManager
                 # For simplicity, we'll start with single keys from above first.

                 model_config = SettingsConfigDict(env_file=".env", extra="ignore")

                 def get_database_url(self) -> str:
                     if self.DATABASE_URL:
                         return self.DATABASE_URL
                     return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

             settings = Settings()
             ```
     *   Verification: Files created. Human creates `.env` from `.env.example` and fills it.

*   `[x]` **P0.7: Setup Basic Logging**
     *   File: `ai_dev_bot_platform/app/core/logging_config.py`
         *   Content:
             ```python
             import logging
             import sys
             from app.core.config import settings

             def setup_logging():
                 logging.basicConfig(
                     level=settings.LOG_LEVEL.upper(),
                     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                     handlers=[
                         logging.StreamHandler(sys.stdout)
                         # Add FileHandler if needed later
                     ]
                 )
                 # You can set specific log levels for libraries here if needed
                 # logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
             ```
     *   Action: In `ai_dev_bot_platform/main.py`, add:
         ```python
         from app.core.logging_config import setup_logging
         # ... other imports ...

         setup_logging() # Call at the beginning
         # ... rest of main.py ...
         ```
     *   Verification: Basic logging setup is present.

*   `[x]` **P0.8: Setup Database Connection (SQLAlchemy)**
     *   File: `ai_dev_bot_platform/app/db/session.py`
         *   Content:
             ```python
             from sqlalchemy import create_engine
             from sqlalchemy.orm import sessionmaker, declarative_base
             from app.core.config import settings

             SQLALCHEMY_DATABASE_URL = settings.get_database_url()

             engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
             SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
             Base = declarative_base()

             # Dependency to get DB session
             def get_db():
                 db = SessionLocal()
                 try:
                     yield db
                 finally:
                     db.close()
             ```
     *   Verification: File created.

*   `[x]` **P0.9: Create Initial `.gitignore`**
     *   File: `ai_dev_bot_platform/.gitignore`
         *   Content:
             ```
             # Byte-compiled / optimized / DLL files
             __pycache__/
             *.py[cod]
             *$py.class

             # C extensions
             *.so

             # Distribution / packaging
             .Python
             build/
             develop-eggs/
             dist/
             downloads/
             eggs/
             .eggs/
             lib/
             lib64/
             parts/
             sdist/
             var/
             wheels/
             *.egg-info/
             .installed.cfg
             *.egg
             MANIFEST

             # PyInstaller
             # Usually these files are created by PyInstaller
             # *.spec
             # *.pyzw
             # *.pyz

             # Installer logs
             pip-log.txt
             pip-delete-this-directory.txt

             # Unit test / coverage reports
             htmlcov/
             .tox/
             .nox/
             .coverage
             .coverage.*
             .cache
             nosetests.xml
             coverage.xml
             *.cover
             *.py,cover
             .hypothesis/
             .pytest_cache/

             # Translations
             *.mo
             *.pot
             *.po

             # Django stuff:
             *.log
             local_settings.py
             db.sqlite3
             db.sqlite3-journal

             # Flask stuff:
             instance/
             .webassets-cache

             # Scrapy stuff:
             .scrapy

             # Sphinx documentation
             docs/_build/

             # PyBuilder
             target/

             # Jupyter Notebook
             .ipynb_checkpoints

             # IPython
             profile_default/
             ipython_config.py

             # PEP 582; __pypackages__
             __pypackages__/

             # Celery stuff
             celerybeat-schedule
             celerybeat.pid

             # SageMath parsed files
             *.sage.py

             # Environments
             .env
             .venv
             env/
             venv/
             ENV/
             env.bak
             venv.bak

             # Spyder project settings
             .spyderproject
             .spyproject

             # Rope project settings
             .ropeproject

             # mkdocs documentation
             /site

             # mypy
             .mypy_cache/
             .dmypy.json
             dmypy.json

             # Pyre type checker
             .pyre/

             # IDEs
             .idea/
             .vscode/
             *.sublime-project
             *.sublime-workspace

             # OS generated files
             .DS_Store
             Thumbs.db

             # Repomix output
             repomix-output.xml
             ```
     *   Verification: File created.

---

## Phase 1: Core Interaction & Basic Orchestration (MVP)

**Goal:** Get the Telegram bot responding, setup basic user model, and lay groundwork for orchestration.

*   `[x]` **P1.1: Define User SQLAlchemy Model & Pydantic Schema**
     *   File: `app/models/user.py`
         *   Content (referencing `high_level_documentation.md` schema):
             ```python
             from sqlalchemy import Column, Integer, String, BigInteger, DateTime, DECIMAL
             from sqlalchemy.sql import func
             from app.db.session import Base

             class User(Base):
                 __tablename__ = "users"
                 id = Column(Integer, primary_key=True, index=True, autoincrement=True)
                 telegram_user_id = Column(BigInteger, unique=True, nullable=False, index=True)
                 username = Column(String(255), nullable=True)
                 email = Column(String(255), nullable=True)
                 credit_balance = Column(DECIMAL(10, 2), nullable=False, default=0.00)
                 created_at = Column(DateTime, default=func.now())
                 updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
             ```
     *   File: `app/schemas/user.py`
         *   Content:
             ```python
             from pydantic import BaseModel, EmailStr
             from typing import Optional
             from decimal import Decimal
             import datetime

             class UserBase(BaseModel):
                 telegram_user_id: int
                 username: Optional[str] = None
                 email: Optional[EmailStr] = None

             class UserCreate(UserBase):
                 pass

             class UserUpdate(BaseModel):
                 username: Optional[str] = None
                 email: Optional[EmailStr] = None
                 credit_balance: Optional[Decimal] = None

             class UserInDBBase(UserBase):
                 id: int
                 credit_balance: Decimal
                 created_at: datetime.datetime
                 updated_at: datetime.datetime

                 class Config:
                     from_attributes = True # Pydantic V2 (formerly orm_mode)

             class User(UserInDBBase):
                 pass
             ```
     *   Verification: Files created.

*   `[x]` **P1.2: Create Database Tables**
     *   Action: In `app/db/init_db.py` (create this file):
         ```python
         from app.db.session import engine, Base
         from app.models.user import User # Import all models here
         # Import other models as they are created
         # from app.models.project import Project
         # from app.models.api_key_models import APIKey, ModelPricing, APIKeyUsage
         # from app.models.transaction import CreditTransaction
         # from app.models.conversation import Conversation
         # from app.models.project_file import ProjectFile

         def init_db():
             # This will create tables if they don't exist.
             # For production, use Alembic migrations.
             Base.metadata.create_all(bind=engine)
             print("Database tables initialized/checked.")

         if __name__ == "__main__":
             init_db()
         ```
     *   Action: Run this script once manually (`python app/db/init_db.py`) after setting up DB.
     *   Verification: `users` table created in PostgreSQL.

*   `[x]` **P1.3: User CRUD Operations (Service Layer)**
     *   File: `app/services/user_service.py`
         *   Content (basic stubs):
             ```python
             from sqlalchemy.orm import Session
             from app.models.user import User
             from app.schemas.user import UserCreate, UserUpdate
             from typing import Optional, List
             from decimal import Decimal

             def get_user_by_telegram_id(db: Session, telegram_user_id: int) -> Optional[User]:
                 return db.query(User).filter(User.telegram_user_id == telegram_user_id).first()

             def create_user(db: Session, user_in: UserCreate, initial_credits: Decimal = Decimal("10.00")) -> User: # Example initial credits
                 db_user = User(
                     telegram_user_id=user_in.telegram_user_id,
                     username=user_in.username,
                     email=user_in.email,
                     credit_balance=initial_credits # Grant initial credits
                 )
                 db.add(db_user)
                 db.commit()
                 db.refresh(db_user)
                 return db_user

             def update_user_credits(db: Session, telegram_user_id: int, amount: Decimal, is_deduction: bool = True) -> Optional[User]:
                 db_user = get_user_by_telegram_id(db, telegram_user_id)
                 if db_user:
                     if is_deduction:
                         if db_user.credit_balance < amount:
                             # Handle insufficient credits (raise error or return None/False)
                             # For now, let's just not deduct if insufficient
                             return None # Or raise an exception
                         db_user.credit_balance -= amount
                     else:
                         db_user.credit_balance += amount
                     db.commit()
                     db.refresh(db_user)
                 return db_user
             # Add other update/get methods as needed
             ```
     *   Verification: File created.

*   `[x]` **P1.4: Basic Telegram Bot Setup & `/start` Command**
     *   File: `app/telegram_bot/handlers.py`
         *   Content:
             ```python
             import logging
             from telegram import Update
             from telegram.ext import ContextTypes, CommandHandler
             from sqlalchemy.orm import Session
             from app.db.session import SessionLocal # For direct session if not using DI from framework
             from app.services import user_service
             from app.schemas.user import UserCreate

             logger = logging.getLogger(__name__)

             async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
                 user_tg = update.effective_user
                 logger.info(f"User {user_tg.id} ({user_tg.username}) started the bot.")

                 db: Session = SessionLocal() # Manual session management for handlers
                 try:
                     user_db = user_service.get_user_by_telegram_id(db, telegram_user_id=user_tg.id)
                     if not user_db:
                         user_in = UserCreate(telegram_user_id=user_tg.id, username=user_tg.username)
                         user_db = user_service.create_user(db, user_in=user_in)
                         await update.message.reply_text(
                             f"Welcome, {user_tg.first_name}! Your account has been created with initial credits: {user_db.credit_balance:.2f}."
                         )
                     else:
                         await update.message.reply_text(
                             f"Welcome back, {user_tg.first_name}! Your credit balance is: {user_db.credit_balance:.2f}."
                         )
                 except Exception as e:
                     logger.error(f"Error in start_command for user {user_tg.id}: {e}", exc_info=True)
                     await update.message.reply_text("Sorry, something went wrong while setting up your account.")
                 finally:
                     db.close()

                 await update.message.reply_text(
                     "I am your AI Development Assistant! Describe your project or use /help for commands."
                 )

             async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
                 await update.message.reply_text(
                     "Available commands:\n"
                     "/start - Start or restart the bot\n"
                     "/help - Show this help message\n"
                     "/status - Check your project status and credits (TODO)\n"
                     # Add more commands as they are implemented
                 )

             # Placeholder for message handler
             async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
                 text = update.message.text
                 logger.info(f"Received message from {update.effective_user.id}: {text}")
                 # TODO: Route to Model Orchestrator
                 await update.message.reply_text(f"Received: '{text}'. Orchestration logic coming soon!")

             # Add more handlers here (e.g., for project descriptions, other commands)
             ```
     *   File: `app/telegram_bot/bot_main.py`
         *   Content:
             ```python
             import logging
             from telegram.ext import Application, CommandHandler, MessageHandler, filters
             from app.core.config import settings
             from app.telegram_bot.handlers import start_command, help_command, message_handler

             logger = logging.getLogger(__name__)

             def run_bot():
                 logger.info("Starting Telegram bot...")
                 application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

                 # Register command handlers
                 application.add_handler(CommandHandler("start", start_command))
                 application.add_handler(CommandHandler("help", help_command))
                 # Add more command handlers here

                 # Register message handler for non-command messages
                 application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

                 logger.info("Telegram bot polling...")
                 application.run_polling()

             if __name__ == "__main__":
                 # This is for running the bot directly (e.g., for development)
                 # In production, this might be managed by a process manager or part of the FastAPI app startup.
                 from app.core.logging_config import setup_logging
                 setup_logging()
                 run_bot()
             ```
     *   Verification: Bot responds to `/start` and `/help`. User record created in DB.

*   `[x]` **P1.5: Model Orchestrator - Basic Structure & Task Routing Stub**
    *   File: `app/services/orchestrator_service.py`
        *   Content (very basic):
            ```python
            import logging
            from sqlalchemy.orm import Session
            from app.schemas.user import User
            # Import agent service stubs later
            # from app.services.architect_agent_service import process_architect_task
            # from app.services.implementer_agent_service import process_implementer_task

            logger = logging.getLogger(__name__)

            class ModelOrchestrator:
                def __init__(self, db: Session):
                    self.db = db
                    # Initialize APIKeyManager here later
                    # self.api_key_manager = APIKeyManager()

                async def process_user_request(self, user: User, user_input: str) -> str:
                    logger.info(f"Orchestrator processing request for user {user.telegram_user_id}: '{user_input}'")

                    # Basic routing logic (placeholder)
                    if "plan" in user_input.lower() or "architect" in user_input.lower():
                        # response = await process_architect_task(self.api_key_manager, user_input) # Stub
                        response = f"Architect Agent would handle: '{user_input}'"
                    elif "implement" in user_input.lower() or "code" in user_input.lower():
                        # response = await process_implementer_task(self.api_key_manager, user_input, codebase_context=None) # Stub
                        response = f"Implementer Agent would handle: '{user_input}'"
                    else:
                        response = "I'm not sure how to handle that yet. Try 'plan' or 'implement'."

                    # TODO: Deduct credits based on agent used and response complexity/tokens
                    # user_service.update_user_credits(self.db, user.telegram_user_id, amount_to_deduct)

                    return response

            # Function to get orchestrator instance (can be improved with DI)
            def get_orchestrator(db: Session) -> ModelOrchestrator:
                return ModelOrchestrator(db)
            ```
    *   Action: Modify `app/telegram_bot/handlers.py` `message_handler`:
        ```python
        # ... imports ...
        from app.services.orchestrator_service import get_orchestrator
        from app.services import user_service # ensure this is imported

        async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            user_tg = update.effective_user
            text = update.message.text
            logger.info(f"Received message from {user_tg.id}: {text}")

            db: Session = SessionLocal()
            try:
                user_db = user_service.get_user_by_telegram_id(db, telegram_user_id=user_tg.id)
                if not user_db: # Should not happen if /start is always first, but good check
                    await update.message.reply_text("Please use /start first to initialize your account.")
                    return

                # Check credits (basic placeholder)
                if user_db.credit_balance <= 0:
                    await update.message.reply_text("You have insufficient credits. Please /credits to add more. (TODO)")
                    return

                orchestrator = get_orchestrator(db)
                response_text = await orchestrator.process_user_request(user=user_db, user_input=text)
                await update.message.reply_text(response_text)

            except Exception as e:
                logger.error(f"Error in message_handler for user {user_tg.id}: {e}", exc_info=True)
                await update.message.reply_text("Sorry, an error occurred while processing your request.")
            finally:
                db.close()
        ```
    *   Verification: Bot responds differently to messages containing "plan" vs "implement".

*   `[ ]` **P1.6: API Key Manager - Basic Structure**
    *   File: `app/services/api_key_manager.py`
        *   Content:
            ```python
            import logging
            from typing import Dict, List, Optional
            from app.core.config import settings # To load keys directly initially

            logger = logging.getLogger(__name__)

            class APIKeyManager:
                def __init__(self):
                    # For simplicity, load directly from settings for now.
                    # Later, this can load from DB, handle encryption, round-robin from pools etc.
                    self.api_keys: Dict[str, List[str]] = {
                        "google": [settings.GOOGLE_API_KEY] if settings.GOOGLE_API_KEY else [],
                        "openrouter": [settings.OPENROUTER_API_KEY] if settings.OPENROUTER_API_KEY else [],
                    }
                    self.current_indices: Dict[str, int] = {
                        provider: 0 for provider in self.api_keys
                    }
                    logger.info("APIKeyManager initialized with keys from settings.")
                    if not self.api_keys["google"] and not self.api_keys["openrouter"]:
                        logger.warning("No API keys configured for Google Gemini or OpenRouter!")


                def get_next_key(self, provider: str) -> Optional[str]:
                    if provider not in self.api_keys or not self.api_keys[provider]:
                        logger.error(f"No API keys available for provider: {provider}")
                        return None

                    keys = self.api_keys[provider]
                    current_index = self.current_indices[provider]
                    key = keys[current_index]
                    self.current_indices[provider] = (current_index + 1) % len(keys)
                    return key

            # Singleton instance or inject as dependency
            # api_key_manager_instance = APIKeyManager()
            ```
    *   Note: The `api_key_manager_instance` would be instantiated and passed to agents by the orchestrator. For now, this class is defined.

---

## Phase 2: Agent Capabilities & Basic Project Flow

**Goal:** Implement basic Architect and Implementer agent logic using LLMs, and introduce the concept of a Project with a TODO list.

*   `[x]` **P2.1: Define Project SQLAlchemy Model & Pydantic Schema**
    *   File: `app/models/project.py`
        *   Content (referencing `high_level_documentation.md`):
            ```python
            import uuid
            from sqlalchemy import Column, Integer, String, DateTime, JSON, TEXT, ForeignKey
            from sqlalchemy.dialects.postgresql import UUID
            from sqlalchemy.sql import func
            from sqlalchemy.orm import relationship
            from app.db.session import Base

            class Project(Base):
                __tablename__ = "projects"
                id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
                user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
                title = Column(String(500), nullable=False, default="Untitled Project")
                description = Column(TEXT, nullable=True)
                status = Column(String(50), default="gathering_requirements") # See high_level_doc for states
                tech_stack = Column(JSON, nullable=True) # e.g., {"language": "python", "framework": "fastapi"}
                current_todo_markdown = Column(TEXT, nullable=True)
                # codebase_index_status (add later)
                # estimated_credit_cost, actual_credit_cost (add with billing)
                created_at = Column(DateTime, default=func.now())
                completed_at = Column(DateTime, nullable=True)

                user = relationship("User") # Define relationship to User model
            ```
    *   File: `app/schemas/project.py`
        *   Content:
            ```python
            from pydantic import BaseModel
            from typing import Optional, Dict, Any
            import uuid
            import datetime

            class ProjectBase(BaseModel):
                title: Optional[str] = "Untitled Project"
                description: Optional[str] = None
                tech_stack: Optional[Dict[str, Any]] = None

            class ProjectCreate(ProjectBase):
                user_id: int # Must be provided by system

            class ProjectUpdate(BaseModel):
                title: Optional[str] = None
                description: Optional[str] = None
                status: Optional[str] = None
                tech_stack: Optional[Dict[str, Any]] = None
                current_todo_markdown: Optional[str] = None
                completed_at: Optional[datetime.datetime] = None

            class ProjectInDBBase(ProjectBase):
                id: uuid.UUID
                user_id: int
                status: str
                current_todo_markdown: Optional[str] = None
                created_at: datetime.datetime
                completed_at: Optional[datetime.datetime] = None
                
                class Config:
                    from_attributes = True

            class Project(ProjectInDBBase):
                pass
            ```
    *   Action: Add `from app.models.project import Project` to `app/db/init_db.py` and re-run to create the table.
    *   Verification: `projects` table created.

*   `[x]` **P2.2: Project CRUD Operations (Service Layer)**
    *   File: `app/services/project_service.py`
        *   Content:
            ```python
            from sqlalchemy.orm import Session
            from app.models.project import Project
            from app.schemas.project import ProjectCreate, ProjectUpdate
            from typing import Optional, List
            import uuid

            def create_project(db: Session, project_in: ProjectCreate, user_id: int) -> Project:
                db_project = Project(
                    user_id=user_id, # Ensure user_id is passed correctly
                    title=project_in.title,
                    description=project_in.description,
                    tech_stack=project_in.tech_stack,
                    status="planning" # Initial status after creation request
                )
                db.add(db_project)
                db.commit()
                db.refresh(db_project)
                return db_project

            def get_project(db: Session, project_id: uuid.UUID) -> Optional[Project]:
                return db.query(Project).filter(Project.id == project_id).first()

            def get_projects_by_user(db: Session, user_id: int) -> List[Project]:
                return db.query(Project).filter(Project.user_id == user_id).all()

            def update_project(db: Session, project_id: uuid.UUID, project_upd: ProjectUpdate) -> Optional[Project]:
                db_project = get_project(db, project_id)
                if db_project:
                    update_data = project_upd.model_dump(exclude_unset=True)
                    for key, value in update_data.items():
                        setattr(db_project, key, value)
                    db.commit()
                    db.refresh(db_project)
                return db_project
            ```
    *   Verification: File created.

*   `[x]` **P2.3: LLM Client Utility**
    *   File: `app/utils/llm_client.py`
        *   Content (basic Gemini and OpenRouter call stubs):
            ```python
            import logging
            import httpx # Using httpx for async calls
            import google.generativeai as genai
            from app.services.api_key_manager import APIKeyManager # Will need instance

            logger = logging.getLogger(__name__)

            # This client will be enhanced significantly
            class LLMClient:
                def __init__(self, api_key_manager: APIKeyManager):
                    self.api_key_manager = api_key_manager
                    self.google_api_key_configured = False
                    # Configure Gemini if key exists
                    google_key = self.api_key_manager.get_next_key("google") # Gets first key
                    if google_key:
                        try:
                            genai.configure(api_key=google_key)
                            self.google_api_key_configured = True
                            logger.info("Google Gemini API configured.")
                        except Exception as e:
                            logger.error(f"Failed to configure Google Gemini API: {e}")
                    else:
                        logger.warning("Google API key not found in APIKeyManager for LLMClient.")


                async def call_gemini(self, prompt: str, model_name: str = "gemini-1.5-flash-latest") -> str: # Use a faster model for testing
                    if not self.google_api_key_configured:
                        return "Error: Google Gemini API not configured."
                    try:
                        # For now, let's assume the API key used for genai.configure() is sufficient
                        # In a multi-key scenario for Google, this would need to pick a key per call
                        # or reconfigure, which is less ideal. ADC is better for Google Cloud.
                        model = genai.GenerativeModel(model_name)
                        response = await model.generate_content_async(prompt) # Async version
                        # Handle potential safety settings blocks if needed based on API response structure
                        if response.parts:
                            return response.text
                        elif response.prompt_feedback and response.prompt_feedback.block_reason:
                            logger.warning(f"Gemini response blocked. Reason: {response.prompt_feedback.block_reason_message}")
                            return f"Error: Content generation blocked by safety settings ({response.prompt_feedback.block_reason_message})."
                        return "Error: No content generated by Gemini or unknown error."
                    except Exception as e:
                        logger.error(f"Error calling Gemini API ({model_name}): {e}", exc_info=True)
                        return f"Error communicating with Gemini: {str(e)}"

                async def call_openrouter(self, model_name: str, prompt: str, system_prompt: Optional[str] = None) -> str:
                    openrouter_key = self.api_key_manager.get_next_key("openrouter")
                    if not openrouter_key:
                        return "Error: OpenRouter API key not configured."

                    headers = {
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json"
                    }
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})
                    
                    data = {
                        "model": model_name, # e.g., "mistralai/mistral-7b-instruct"
                        "messages": messages
                    }
                    api_url = "https://openrouter.ai/api/v1/chat/completions"

                    try:
                        async with httpx.AsyncClient(timeout=120.0) as client: # Increased timeout
                            response = await client.post(api_url, headers=headers, json=data)
                            response.raise_for_status() # Raise an exception for bad status codes
                            result = response.json()
                            if result.get("choices") and result["choices"][0].get("message"):
                                return result["choices"][0]["message"]["content"]
                            logger.error(f"Unexpected OpenRouter response format: {result}")
                            return "Error: Unexpected response format from OpenRouter."
                    except httpx.HTTPStatusError as e:
                        logger.error(f"HTTP error calling OpenRouter API ({model_name}): {e.response.status_code} - {e.response.text}", exc_info=True)
                        return f"Error with OpenRouter API ({e.response.status_code}): {e.response.text}"
                    except Exception as e:
                        logger.error(f"Error calling OpenRouter API ({model_name}): {e}", exc_info=True)
                        return f"Error communicating with OpenRouter: {str(e)}"

            ```
    *   Verification: File created.

*   `[x]` **P2.4: Architect Agent Service - Basic Planning**
    *   File: `app/agents/architect_agent.py`
        *   Content:
            ```python
            import logging
            from app.utils.llm_client import LLMClient
            from app.schemas.project import Project # For type hinting if needed

            logger = logging.getLogger(__name__)

            class ArchitectAgent:
                def __init__(self, llm_client: LLMClient):
                    self.llm_client = llm_client

                async def generate_initial_plan_and_docs(self, project_requirements: str, project_title: str) -> dict:
                    logger.info(f"Architect Agent: Generating plan for '{project_title}'")
                    # Using Gemini for planning
                    # More sophisticated prompt engineering needed here
                    prompt = f"""
                    You are an expert software architect. Based on the following project requirements for a project titled '{project_title}',
                    generate:
                    1. A brief technical overview/architecture document (Markdown).
                    2. A preliminary technology stack suggestion (list form).
                    3. A detailed TODO list in Markdown format for a small LLM (4B model) to implement the project.
                       The TODO list should be broken down into small, actionable steps.
                       Mark each item like this: `[ ] Task description`.

                    Project Requirements:
                    {project_requirements}

                    Output format should be structured clearly with headings for each section.
                    Start the TODO list with '### Implementation TODO List'.
                    """
                    # Example model choice - could be configurable
                    response_text = await self.llm_client.call_gemini(prompt, model_name="gemini-1.5-pro-latest") # Use a powerful model

                    if response_text.startswith("Error:"):
                        logger.error(f"Architect Agent: Error from LLM: {response_text}")
                        return {"error": response_text}

                    # Basic parsing (very simplistic, needs improvement)
                    # This parsing logic will be complex and error-prone for a 4B model to write reliably.
                    # Human review or a more capable LLM would be needed for robust parsing.
                    try:
                        # This is a placeholder for more robust parsing.
                        # For a 4B model, we might just return the raw text and let the orchestrator
                        # or a human split it. Or, ask the LLM to output JSON.
                        doc_content = response_text # For now, assume entire response is the doc.
                        todo_list_md = ""
                        tech_stack_str = "Tech stack not extracted." # Placeholder

                        if "### Implementation TODO List" in response_text:
                            parts = response_text.split("### Implementation TODO List", 1)
                            doc_content = parts[0].strip()
                            todo_list_md = "### Implementation TODO List\n" + parts[1].strip() if len(parts) > 1 else ""
                        
                        # Simplistic tech stack extraction (example, very fragile)
                        if "technology stack suggestion" in doc_content.lower():
                            # ... placeholder for extraction logic ...
                            pass


                        return {
                            "documentation": doc_content,
                            "tech_stack_suggestion": tech_stack_str, # Placeholder
                            "todo_list_markdown": todo_list_md
                        }
                    except Exception as e:
                        logger.error(f"Architect Agent: Error parsing LLM response: {e}", exc_info=True)
                        return {"error": "Failed to parse LLM response for plan."}

                async def verify_implementation_step(self, project: Project, code_snippet: str, relevant_docs: str, todo_item: str) -> dict:
                    logger.info(f"Architect Agent: Verifying step for project {project.id}: '{todo_item}'")
                    # Placeholder for verification logic
                    prompt = f"""
                    You are an expert code reviewer and software architect.
                    Project Title: {project.title}
                    Project Description: {project.description}
                    Relevant Documentation/Architecture:
                    {relevant_docs}

                    The task was: '{todo_item}'
                    The implemented code is:
                    ```
                    {code_snippet}
                    ```
                    Does this code correctly implement the task according to the project context and best practices?
                    Provide feedback: 'APPROVED' or 'REJECTED: [detailed reasons and suggestions]'.
                    If REJECTED, suggest updates to the code or the TODO list.
                    """
                    # Use a capable model for verification
                    response_text = await self.llm_client.call_gemini(prompt, model_name="gemini-1.5-pro-latest")
                    
                    if response_text.startswith("Error:"):
                         return {"status": "ERROR", "feedback": response_text}
                    
                    if "APPROVED" in response_text.upper():
                        return {"status": "APPROVED", "feedback": response_text}
                    else:
                        return {"status": "REJECTED", "feedback": response_text}

            ```
    *   Verification: File created.

*   `[x]` **P2.5: Implementer Agent Service - Basic Code Generation**
    *   File: `app/agents/implementer_agent.py`
        *   Content:
            ```python
            import logging
            from app.utils.llm_client import LLMClient
            # from app.services.codebase_indexing_service import CodebaseIndex # Import later

            logger = logging.getLogger(__name__)

            class ImplementerAgent:
                def __init__(self, llm_client: LLMClient): # Add codebase_index: Optional[CodebaseIndex] = None later
                    self.llm_client = llm_client
                    # self.codebase_index = codebase_index

                async def implement_todo_item(self, todo_item: str, project_context: str, tech_stack: dict) -> dict:
                    logger.info(f"Implementer Agent: Implementing TODO: '{todo_item}'")
                    # Using OpenRouter for diverse coding models, or a code-specific Gemini model
                    # Tech stack information
                    lang = tech_stack.get("language", "python") # Default to python
                    framework = tech_stack.get("framework", "")
                    
                    # Context for the LLM
                    # if self.codebase_index and project_id: # project_id would be needed
                    #    relevant_code = self.codebase_index.query(todo_item, project_id=project_id) # Simplified
                    # else:
                    #    relevant_code = "No existing code context available."
                    relevant_code = "No existing code context available for this initial version."


                    prompt = f"""
                    You are an expert software developer. Your task is to implement the following TODO item for a project.
                    Project Context:
                    {project_context}

                    Technology Stack: Language: {lang}, Framework: {framework if framework else 'N/A'}

                    Relevant existing code snippets (if any, use as reference):
                    {relevant_code}

                    TODO Item to Implement:
                    '{todo_item}'

                    Provide only the code for this specific task.
                    If the task involves creating a new file, indicate the filename in a comment like '# FILENAME: path/to/file.ext'.
                    If it's modifying an existing file, try to provide the complete updated file or a clear diff/patch.
                    Ensure the code is clean, follows best practices for {lang}, and directly addresses the task.
                    Do not include explanations unless specifically asked for in the TODO item.
                    """

                    # Example model choice via OpenRouter - could be configurable or selected by orchestrator
                    # Or use a code-specific Gemini model if available and configured
                    # model_to_use = "anthropic/claude-3-haiku-20240307" # Cheaper, faster for simple tasks
                    # model_to_use = "deepseek/deepseek-coder-v2-lite-instruct"
                    model_to_use = "mistralai/mistral-7b-instruct" # A good general small model on OpenRouter
                    # model_to_use = "gemini-1.0-pro" # If using Gemini for coding

                    # response_text = await self.llm_client.call_gemini(prompt, model_name=model_to_use) # if using Gemini
                    response_text = await self.llm_client.call_openrouter(model_name=model_to_use, prompt=prompt)


                    if response_text.startswith("Error:"):
                        logger.error(f"Implementer Agent: Error from LLM: {response_text}")
                        return {"error": response_text, "code": None, "filename": None}

                    # Basic filename extraction (very simplistic)
                    filename = None
                    code_content = response_text
                    if "# FILENAME:" in response_text:
                        try:
                            header, content_part = response_text.split("\n", 1)
                            if header.startswith("# FILENAME:"):
                                filename = header.split("# FILENAME:", 1)[1].strip()
                                code_content = content_part
                        except ValueError: # If no newline after filename comment
                            if response_text.startswith("# FILENAME:"):
                                filename = response_text.split("# FILENAME:",1)[1].strip()
                                code_content = "" # Assume only filename was given
                    
                    return {"code": code_content.strip(), "filename": filename, "error": None}
            ```
    *   Verification: File created.

*   `[x]` **P2.6: Update Model Orchestrator to use Agents & Projects**
     *   File: `app/services/orchestrator_service.py`
     *   Action: Refactor significantly.
     *   Key Logic:
         *   Initialize `APIKeyManager` and `LLMClient`.
         *   Initialize `ArchitectAgent` and `ImplementerAgent` with the `LLMClient`.
         *   `process_user_request`:
             *   If it's a new project description:
                 *   Call `project_service.create_project`.
                 *   Call `architect_agent.generate_initial_plan_and_docs`.
                 *   Store documentation and TODO list in the `Project` model using `project_service.update_project`.
                 *   Return a summary and part of the TODO list to the user.
             *   If it's a command to proceed with a TODO item (e.g., user says "implement task 1 of project XYZ"):
                 *   Retrieve project and its `current_todo_markdown`.
                 *   Identify the next `[ ]` task.
                 *   Call `implementer_agent.implement_todo_item` with task, project context, tech stack.
                 *   Store generated code (how/where to store this is a big step - for now, maybe just log it or add to a temporary `project_files` structure).
                 *   Update the TODO item to `[x]` in `current_todo_markdown` (simple string replace for now).
                 *   (Verification step will be added in Phase 3).
             *   Update `project.status` accordingly (e.g., 'planning', 'implementing', 'awaiting_verification').
     *   Verification: Orchestrator can create a project, generate a plan via Architect, and (conceptually) delegate a TODO item to Implementer.

*   `[x]` **P2.7: Define `project_files` SQLAlchemy Model & Pydantic Schema**
     *   File: `app/models/project_file.py`
         *   Content:
             ```python
             import uuid
             from sqlalchemy import Column, TEXT, String, DateTime, ForeignKey
             from sqlalchemy.dialects.postgresql import UUID
             from sqlalchemy.sql import func
             from sqlalchemy.orm import relationship
             from app.db.session import Base

             class ProjectFile(Base):
                 __tablename__ = "project_files"
                 id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
                 project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
                 file_path = Column(String(1000), nullable=False) # e.g., "src/main.py"
                 file_type = Column(String(100), nullable=True) # e.g., "python", "markdown"
                 content = Column(TEXT, nullable=True)
                 created_at = Column(DateTime, default=func.now())
                 updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

                 project = relationship("Project")
             ```
     *   File: `app/schemas/project_file.py`
         *   Content:
             ```python
             from pydantic import BaseModel
             from typing import Optional
             import uuid
             import datetime

             class ProjectFileBase(BaseModel):
                 file_path: str
                 content: str
                 file_type: Optional[str] = None

             class ProjectFileCreate(ProjectFileBase):
                 project_id: uuid.UUID # System provided

             class ProjectFileUpdate(BaseModel):
                 content: Optional[str] = None
                 file_path: Optional[str] = None # Should path be updatable? Usually not.

             class ProjectFileInDBBase(ProjectFileBase):
                 id: uuid.UUID
                 project_id: uuid.UUID
                 created_at: datetime.datetime
                 updated_at: datetime.datetime

                 class Config:
                     from_attributes = True
             
             class ProjectFile(ProjectFileInDBBase):
                 pass
             ```
     *   Action: Add to `init_db.py` and run.
     *   Verification: Table created.

*   `[x]` **P2.8: `project_file_service.py` CRUD Operations**
     *   File: `app/services/project_file_service.py`
         *   Content: Basic CRUD (create, get by path, get all for project, update content).
     *   Verification: Service file created.

---

**Note:** Phases 3-6 would follow a similar pattern of defining models, services, agent logic, and orchestrator updates. This initial set provides a very detailed start for the first major hurdles. Human oversight will be critical for guiding the 4B LLM, especially with complex parsing, state management in the orchestrator, and robust error handling.

This plan is already very long. Subsequent phases would cover:
*   **Phase 3: Codebase Indexing, Verification Loop & Basic Aider Integration:**
    *   Vector DB setup (e.g., FAISS locally or cloud service).
    *   Codebase Indexing Service (`app/services/codebase_indexing_service.py`).
    *   Orchestrator calls Architect for verification after Implementer.
    *   Implementer uses Aider (basic command execution via subprocess) for applying changes.
*   **Phase 4: Monetization & User Management Details:**
    *   `model_pricing`, `api_key_usage`, `credit_transactions` models and services.
    *   Accurate credit deduction in Orchestrator for Gemini & OpenRouter calls.
    *   `/credits` command, `/status` command enhancements.
*   **Phase 5: Polish, `README.md` Generation (for user projects) & Pre-Production Testing:**
    *   Architect Agent generates `README.md` for the *user's generated project*.
    *   Refine error handling, logging.
    *   More comprehensive manual testing of full flows.
*   **Phase 6: Dockerization, Basic K8s Manifests & Deployment Prep:**
    *   `Dockerfile` for the main application (FastAPI + Telegram Bot + Celery Worker in one image, or separate images).
    *   `docker-compose.yml` for local development.
    *   Basic Kubernetes `Deployment` and `Service` YAMLs for key components.
    *   Refine environment variable handling for K8s (ConfigMaps, Secrets).

This level of detail is necessary for a smaller LLM. Each `[ ]` is a promptable unit of work, with the surrounding context provided. Good luck!