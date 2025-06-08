
# AI-Powered Development Assistant Telegram Bot

## Project Overview

This Telegram bot serves as an autonomous software development assistant that takes user requirements and delivers complete, production-ready applications. The bot leverages a sophisticated **Model Orchestrator** that intelligently routes tasks to either a **large "Architect" Language Model (LLM)** for planning, documentation, and verification, or **smaller "Implementer" LLMs** for code execution, utilizing models accessed directly from **Google Gemini** and a diverse range via **OpenRouter**. A key component enhancing this process is **codebase indexing**, which provides deep contextual understanding of the generated code for more accurate implementation and verification. Upon project completion, a detailed `README.md` with setup and usage instructions is automatically generated. The system incorporates a **credit-based monetization model**, providing initial free credits and requiring users to purchase additional credits for continued use, all managed through a diligent cost-tracking mechanism.

## Core Functionality

The bot transforms user ideas into complete software projects by:
- Gathering detailed requirements through conversational interfaces.
- **Utilizing the Model Orchestrator to decide which specialized agent (Architect or Implementer) to engage.**
- **Employing an Architect LLM to generate comprehensive technical documentation based on software development best practices.**
- Selecting optimal technology stacks (Architect LLM).
- **Having the Architect LLM create detailed, actionable TODO markdown list plans for Implementer LLMs.**
- **Leveraging a codebase indexing service to maintain an up-to-date, searchable representation of the project's code, enabling context-aware operations for both Architect and Implementer LLMs.**
- **Employing Implementer LLMs to systematically execute tasks from the TODO list, referencing the codebase index for context and marking items as complete (`[x]`) upon implementation.**
- **Incorporating verification cycles where the Architect LLM meticulously reviews the work done by Implementer LLMs. This verification cross-references the `TODO list`, `project requirements`, `technical documentation`, and the actual `codebase (via the index)` to ensure alignment and quality.**
- Automatically implementing the entire codebase through this iterative process.
- **Automatically generating a comprehensive `README.md` file upon project completion, detailing setup, configuration, and execution steps for the developed application.**
- **Managing user access through a credit system: initial free credits are provided, with subsequent usage requiring credit purchases.**
- **Diligently tracking LLM API usage costs to inform user billing (credit deduction) and ensure platform profitability.**
- Delivering packaged applications via Telegram.

## User Journey Flow

### **Phase 1: Requirement Gathering**
1.  **Initial Contact & Credit Check**: User starts bot with `/start`. System checks/grants initial credits. If insufficient credits for a new project, prompts for purchase.
2.  **Project Description**: User provides initial app description.
3.  **Intelligent Questioning**: Bot (Orchestrator leveraging an appropriate LLM) asks targeted follow-up questions about:
    *   Target audience and use cases
    *   Preferred platforms (web, mobile, desktop)
    *   Specific features and functionality
    *   Performance and scalability requirements
    *   Integration needs
    *   Budget and timeline constraints

### **Phase 2: Analysis and Planning (Architect LLM Driven, Orchestrated)**
4.  **Requirement Analysis**: The Orchestrator engages the **Architect LLM** to process all gathered information.
5.  **Technology Stack Selection**: Architect LLM selects optimal tech stack.
6.  **Project Architecture**: Architect LLM creates high-level system design.
7.  **Documentation & Plan Generation**:
    *   The **Architect LLM** generates comprehensive project documentation (requirements, architecture, etc.) adhering to best practices.
    *   The **Architect LLM** then creates a detailed **TODO markdown list** (`TODO.md`) outlining the implementation steps.

### **Phase 3: Iterative Implementation & Verification (Orchestrator, Implementer LLMs, Architect LLM, Codebase Indexing)**
8.  **Development Kickoff & Cost Estimation (Optional)**: Bot notifies user that development has started. May provide a rough credit estimate for the project based on complexity.
9.  **Repository Creation & Indexing**: Git repository created. **The codebase indexing service begins monitoring this repository.**
10. **Iterative Code Generation & Task Completion**:
    *   The **Model Orchestrator** assigns tasks from `TODO.md` to **Implementer LLMs**.
    *   Implementer LLMs use tools like Aider to implement code for each task, potentially querying the **codebase index** for relevant existing code context.
    *   Upon completing a task, the Implementer LLM updates `TODO.md` (e.g., `[ ] Task 1` becomes `[x] Task 1`) and commits changes. **API usage is logged, and corresponding credits are deducted from the user's balance.**
    *   **The codebase indexing service updates its index with the new changes.**
11. **Verification Cycles**:
    *   After a predefined phase or set of TODO items are completed, the **Orchestrator** triggers a verification step, engaging the **Architect LLM**.
    *   The **Architect LLM** verifies the implemented work by analyzing:
        *   The completed items in the `TODO.md`.
        *   The original `project requirements`.
        *   The `technical documentation` (including architecture design).
        *   The current state of the **`codebase` (accessed via the codebase index)**.
    *   **Architect LLM usage also incurs credit costs.** If issues are found, the Architect LLM provides feedback (potentially by adding new or revised TODOs) for the Implementer LLMs. If all is correct, the Orchestrator allows the process to continue.
12. **Progress & Credit Updates**: Periodic notifications to user about development progress and current credit consumption.

### **Phase 4: Delivery & Finalization**
13. **Final Quality Assurance**: Includes automated testing, a final code review, and a conclusive verification pass by the **Architect LLM** (using the codebase index and all documentation).
14. **`README.md` Generation**: The **Architect LLM** (or a specialized documentation model) generates a detailed `README.md` file for the project, including:
    *   Project overview.
    *   Prerequisites (languages, frameworks, tools).
    *   Installation steps (cloning, dependency installation).
    *   Configuration guide (environment variables, settings).
    *   How to run the application (development server, build commands, production deployment notes if applicable).
    *   Key features and basic usage examples.
    *   Directory structure overview (optional).
15. **Package Creation**: Generates downloadable project package (including the new `README.md`).
16. **Delivery**: Sends ZIP file to user via Telegram. User is notified of final credit cost for the project.

## Technical Architecture

### **Core Components**

**Telegram Bot Interface**
- Built using `python-telegram-bot` library.
- Handles user interactions, file delivery, and credit purchase prompts.

**Model Orchestrator**
- **The central decision-making unit for AI agent deployment.**
- **Primary Role: Task Router.** Based on the current project phase and task type, it decides whether to engage the "Architect" agent/LLM or an "Implementer" agent/LLM.
- Manages the overall workflow, including the iterative implementation-verification loop and integration with the Cost Management & Billing System.
- Integrates with the `APIKeyManager` and the `Codebase Indexing Service`.

**Architect Agent/LLM**
- Utilizes powerful models (e.g., Gemini 1.5 Pro accessed directly, or high-capability models like Claude 3 Opus via OpenRouter).
- **Responsibilities (when invoked by Orchestrator):**
    - High-level planning and architectural decisions.
    - Generating comprehensive documentation (requirements, architecture, best practices).
    - Creating detailed **markdown TODO lists** for implementation.
    - **Verifying implemented code:** Critically analyzes the work of Implementer LLMs by comparing the `TODO list`, `project requirements`, and `technical documentation` against the actual `codebase` (accessed via the `Codebase Indexing Service`).
    - **Generating the final `README.md` file for the project.**

**Implementer Agent/LLMs**
- Employs smaller, efficient coding models (e.g., code-specific Gemini models, or models like DeepSeek Coder, Phind CodeLlama accessed via OpenRouter).
- **Responsibilities (when invoked by Orchestrator):**
    - Executing specific coding tasks from the TODO list.
    - Interacting with tools like Aider for code generation and modification.
    - **Potentially leveraging the `Codebase Indexing Service` to understand existing code context relevant to the current task.**
    - Marking TODO items with `[x]` upon completion and committing code.

**Codebase Indexing Service**
- **Maintains a searchable, semantic index of the project's entire codebase.**
- **Mechanism:** Continuously (or on-commit) parses the codebase, generates vector embeddings for code chunks, and stores them in a vector database.
- **Benefits:** Provides **Architect LLM** with accurate context for verification and **Implementer LLMs** with relevant code snippets.

**Code Generation Engine**
- **Aider Integration**: Primary tool used by **Implementer LLMs**.
- **Git Management**: Automated repository creation, version control. Commits trigger codebase indexing updates.
- **Multi-language Support**.

**Documentation Generator**
- **Primarily driven by the Architect LLM.**
- Outputs include requirements, architecture, API docs, the `TODO.md` plan, and the final `README.md`.

**Cost Management & Billing System**
- **Credit Management**: Handles user credit balances (initial grants, purchases, deductions).
- **Usage Tracking**: Logs every LLM API call, associated token counts (input/output), the specific model used, and calculates the cost via the `api_key_usage` and `model_pricing` tables.
- **Cost Calculation**:
    - Retrieves per-model pricing from the `model_pricing` table.
    - Calculates the actual cost incurred by the company for each API call.
    - Determines the number of credits to deduct from the user based on the actual cost and a predefined markup/conversion rate.
- **Billing Integration (Future)**: Interface with payment gateways (e.g., Stripe, PayPal) for credit purchases.
- **Reporting**: Generates reports on API expenditures, revenue from credit sales, and user consumption patterns.

### **API Key Management System**
- **Round-Robin Distribution Strategy**: Distributes requests across multiple keys for Google Cloud (for Gemini models) and OpenRouter to optimize performance and reduce rate limiting.
- **Provider-Specific Key Pools**:
  ```python
  # Separate key pools for each AI provider
  API_KEY_POOLS = {
      'google': ['gemini_key1', 'gemini_key2', 'gemini_key3'], # For direct Gemini access
      'openrouter': ['or_key1', 'or_key2', 'or_key3']       # For OpenRouter access
      # Potentially other direct providers if added in the future
  }
  ```
- **Key Rotation and Security**: Automated rotation, usage monitoring, rate limit management, and failover mechanisms.

### **Technology Stack**

**Backend Infrastructure**
```python
# Core Technologies
- Python 3.12+ (Bot implementation, Model Orchestrator, Agents)
- FastAPI (API endpoints)
- SQLAlchemy (Database ORM)
- Redis (Session management, caching, potentially task queueing)
- Celery (Background task processing for LLM interactions and indexing)
- Vector Database (e.g., Pinecone, Weaviate, Milvus, or self-hosted FAISS) for Codebase Indexing Service
- Payment Gateway SDKs (e.g., Stripe Python library for future billing)
```

**AI Integration**
```python
# AI Model APIs managed by Orchestrator & APIKeyManager
# Direct Provider Access:
- Google Gemini (e.g., Gemini 1.5 Pro, Gemini 1.0 Ultra, code-specific Gemini models) for planning, architecture, verification, and specialized tasks.
# Aggregator Access:
- OpenRouter (Unified API access to a variety of models including those from Anthropic, OpenAI, Mistral AI, etc., for flexible task execution, implementation, or specialized documentation tasks).
# Code Embedding Models (can be sourced via OpenRouter or dedicated providers)
- e.g., Google's gecko-embeddings, or models like Jina Embeddings, Sentence Transformers available through OpenRouter or hosted.
# Model usage details for Google and OpenRouter are stored for cost calculation.
```

**Development Tools**
```bash
# Code Generation & Version Control
- Aider (AI pair programming by Implementer LLMs)
- Git (Version control, triggers codebase indexing)
- Docker (Containerization)
- GitHub/GitLab APIs (Repository management - optional)
```

## Database Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_user_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    email VARCHAR(255) NULL, -- For billing and notifications
    credit_balance DECIMAL(10, 2) DEFAULT 0.00 NOT NULL, -- Platform-specific credits
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'gathering_requirements', -- e.g., gathering_requirements, planning, implementing, verifying, readme_generation, completed, failed
    tech_stack JSONB,
    current_todo_markdown TEXT,
    codebase_index_status VARCHAR(50) DEFAULT 'not_indexed', -- e.g., not_indexed, indexing, indexed, error
    estimated_credit_cost DECIMAL(10, 2) NULL,
    actual_credit_cost DECIMAL(10, 2) NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(100) NOT NULL,
    key_identifier VARCHAR(255) NOT NULL,
    encrypted_key TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE TABLE model_pricing (
    id SERIAL PRIMARY KEY,
    model_provider VARCHAR(100) NOT NULL, -- e.g., 'google', 'openrouter'
    model_name VARCHAR(255) NOT NULL UNIQUE, -- e.g., 'gemini-1.5-pro-latest', 'openrouter/anthropic/claude-3-opus'
    input_cost_per_million_tokens DECIMAL(12, 6) NOT NULL,
    output_cost_per_million_tokens DECIMAL(12, 6) NOT NULL,
    image_input_cost_per_image DECIMAL(12, 6) NULL, -- For multimodal
    image_output_cost_per_image DECIMAL(12, 6) NULL, -- If applicable
    currency VARCHAR(10) DEFAULT 'USD' NOT NULL,
    notes TEXT, -- e.g., "Pricing effective YYYY-MM-DD", "Context window size"
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE api_key_usage (
    id SERIAL PRIMARY KEY,
    project_id UUID REFERENCES projects(id) NULL,
    user_id INTEGER REFERENCES users(id) NULL, -- For easier querying of user-specific costs
    api_key_id INTEGER REFERENCES api_keys(id),
    model_name VARCHAR(255) NOT NULL, -- Specific model used, e.g., 'gemini-1.5-pro-latest', or 'openrouter/path/to/model'
    task_type VARCHAR(100), -- e.g., 'planning', 'coding', 'verification', 'readme_generation', 'code_embedding'
    input_tokens_used INTEGER DEFAULT 0,
    output_tokens_used INTEGER DEFAULT 0,
    images_processed INTEGER DEFAULT 0, -- For multimodal models
    actual_cost_usd DECIMAL(10, 6), -- Calculated cost to the company based on model_pricing
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE credit_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    project_id UUID REFERENCES projects(id) NULL,
    api_key_usage_id INTEGER REFERENCES api_key_usage(id) NULL, -- Link to specific API call if deduction
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN ('initial_grant', 'purchase', 'usage_deduction', 'refund', 'manual_adjustment', 'referral_bonus')),
    credits_amount DECIMAL(10, 2) NOT NULL, -- Positive for additions, negative for deductions
    real_cost_associated_usd DECIMAL(10, 6) NULL, -- If 'usage_deduction', stores the company's cost for that usage
    external_transaction_id VARCHAR(255) NULL, -- e.g., Stripe charge ID for purchases
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    message_type VARCHAR(50), -- 'user_message', 'bot_question', 'bot_update'
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE project_files (
    id SERIAL PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    file_path VARCHAR(1000),
    file_type VARCHAR(100),
    content TEXT, -- Or reference to storage if large
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Implementation Architecture

### **Bot Command Structure**
```python
# Core bot commands and handlers
/start - Initialize new project, check credits
/status - Check current project status and credit usage
/cancel - Cancel current project (with credit considerations)
/help - Show available commands
/credits - View credit balance and purchase options
/history - View past projects
/keys - Show API key status (admin only)
```

### **Conversation State Management**
```python
# Conversation states for multi-step interactions
STATES = {
    'INITIALIZING': 'checking_credits_or_prompting_purchase',
    'GATHERING_REQUIREMENTS': 'collecting_initial_info',
    'CLARIFYING_DETAILS': 'asking_followup_questions',
    'CONFIRMING_SCOPE': 'final_confirmation_before_planning',
    'PLANNING': 'architect_llm_planning_and_doc_generation',
    'IMPLEMENTING_VERIFYING': 'iterative_coding_and_verification_loop',
    'FINALIZING': 'readme_generation_and_packaging',
    'DELIVERY': 'sending_final_package'
}
```

### **AI Model Orchestration Logic**
The Model Orchestrator uses project state and task type to route requests to the Architect or Implementer LLM, providing necessary context (requirements, TODOs, codebase index access). It also triggers credit deductions via the Cost Management System after each billable LLM operation.

### **Cost Calculation & Credit Deduction Flow (Conceptual):**
1.  LLM API call is made (e.g., by Architect or Implementer agent).
2.  After the call, `input_tokens`, `output_tokens`, and `model_name` are recorded.
3.  System queries `model_pricing` for the `model_name` to get `input_cost_per_million_tokens` and `output_cost_per_million_tokens`.
4.  `actual_cost_usd` = (input_tokens / 1,000,000 * input_cost) + (output_tokens / 1,000,000 * output_cost).
5.  This `actual_cost_usd` is logged in `api_key_usage`.
6.  `credits_to_deduct` = (`actual_cost_usd` / `PLATFORM_CREDIT_VALUE_USD`) * `MARKUP_FACTOR`.
    *   `PLATFORM_CREDIT_VALUE_USD`: A system constant, e.g., 1 credit = $0.01.
    *   `MARKUP_FACTOR`: A system constant, e.g., 1.5 (for a 50% markup).
7.  User's `credit_balance` in the `users` table is reduced by `credits_to_deduct`.
8.  A new record is inserted into `credit_transactions` detailing the deduction.
9.  If `credit_balance` falls below a threshold, the user might be warned or operations paused until credits are replenished.

## Key Features and Capabilities

### **Intelligent Requirement Gathering**
- Context-aware follow-up questions for comprehensive understanding.

### **Hierarchical AI Collaboration (Orchestrator, Architect, Implementer)**
- **Model Orchestrator** for strategic task routing.
- **Architect LLM** for planning, documentation, `README.md` generation, and rigorous verification.
- **Implementer LLMs** for focused, context-aware code execution.

### **Context-Aware Codebase Understanding**
- **Dedicated Codebase Indexing Service** provides semantic search capabilities over the evolving codebase.
- Enhances accuracy for both Architect (verification) and Implementer LLMs (implementation).

### **Technology Stack Optimization (Architect LLM)**
- Requirements-based selection of optimal technologies.

### **Comprehensive Documentation (Architect LLM Driven)**
- Includes project requirements, architecture, API docs, a versioned `TODO.md`, and a user-friendly `README.md`.

### **Automated `README.md` Generation**
- The Architect LLM, at project completion, crafts a detailed `README.md`.
- Includes sections for project overview, prerequisites, installation, configuration, and usage instructions, tailored to the generated application.

### **Credit-Based Monetization & Cost Tracking**
- **User Credits**: Users operate on a credit system, receiving an initial free quota (e.g., enough for one small project).
- **Transparent Costing**: Efforts to inform users about potential credit consumption; detailed transaction history available.
- **Detailed Usage Logging**: All LLM API calls (including embedding generation) are logged with token counts and associated models.
- **Accurate Cost Calculation**: System calculates actual API costs based on up-to-date `model_pricing`.
- **Profit Margin Management**: A configurable markup is applied to actual costs to determine user credit deduction, ensuring platform sustainability and profitability.
- **Credit Purchase Options**: Users can purchase additional credits to continue using the service.

### **Rigorous Quality Assurance & Verification**
- **Architect LLM performs verification by comparing `TODOs`, `requirements`, and `documentation` against the actual `codebase` (via its index).**
- Integration of automated testing and security scanning is envisioned.

## File Management and Delivery

### **Project Structure Generation**
```
generated_project/
├── .code_index/  <-- (Conceptual, managed by Codebase Indexing Service, may not be user-visible)
├── docs/
│   ├── requirements.md
│   ├── architecture.md
│   ├── api_documentation.md
│   └── deployment_guide.md
├── src/
│   ├── frontend/
│   ├── backend/
│   └── database/
├── tests/
├── docker-compose.yml
├── README.md       <-- NEW: Automatically generated, comprehensive user guide
├── TODO.md       <-- Central plan, updated by Implementers, verified by Architect
└── .gitignore
```
### **Delivery Mechanism**
- Automated ZIP file creation of the `generated_project` directory.
- Secure file transfer via Telegram.
- Optionally, provide a link to a (temporary) Git repository.

## Security and Privacy

### **Data Protection**
- End-to-end encryption for sensitive data where applicable.
- Automatic data purging policies for completed projects after a defined period (user-configurable).
- Encrypted API key storage (e.g., AES-256).
- User privacy compliance (GDPR/CCPA considerations).
- **Secure handling of billing information**: If credit card details are processed directly, PCI DSS compliance is mandatory. Offloading to reputable payment processors (e.g., Stripe, PayPal) is highly recommended.

### **Access Control**
- User authentication via Telegram.
- Project ownership verification.
- Rate limiting and abuse prevention mechanisms.
- Secure API key rotation.

## Monitoring and Analytics

### **Performance Metrics**
- Project completion rates and times.
- User satisfaction scores (via feedback mechanisms).
- AI agent performance (e.g., verification pass/fail rates, task completion times).
- Codebase indexing efficiency.

### **Cost Management & Revenue Analytics**
- **Real-time API Expenditure Tracking**: Monitor costs per provider, per model, per project, and per user from `api_key_usage` and `model_pricing`.
- **Credit Consumption Patterns**: Analyze how users spend credits, identify high-cost features or LLM tasks.
- **Profitability Analysis**: Track revenue from credit sales (via `credit_transactions` of type 'purchase') vs. API costs to determine net profit margins.
- **Pricing Model Effectiveness**: Evaluate if the current `model_pricing` and `MARKUP_FACTOR` are optimal.
- **User Churn vs. Credit Usage**: Correlate credit depletion with user activity and identify points for intervention or offers.
- Alerts for unusual cost spikes or low global API key quotas.

## Deployment Architecture

### **Infrastructure Requirements**
```yaml
# Docker Compose example
services:
  telegram_bot:
    image: ai-dev-bot:latest
    environment:
      - TELEGRAM_BOT_TOKEN=${BOT_TOKEN}
      - DATABASE_URL=${DB_URL}
      - REDIS_URL=${REDIS_URL}
      - API_KEY_ENCRYPTION_KEY=${ENCRYPTION_KEY}
  model_orchestrator:
    image: ai-dev-bot-orchestrator:latest
    # ... environment variables for LLM access, task queue, etc.
  architect_agent_service: # Potentially if Architect LLM tasks are long-running or resource-intensive
    image: ai-dev-bot-architect:latest
    # ...
  implementer_agent_worker: # Celery worker for Implementer LLMs
    image: ai-dev-bot-implementer-worker:latest
    command: celery worker -Q implementation_tasks
    # ...
  codebase_indexing_service:
    image: ai-dev-bot-code-indexer:latest
    environment:
      - VECTOR_DB_URL=${VECTOR_DB_URL}
    volumes:
      - ./project_repositories:/mnt/repos # Example path for code access
  vector_database: # e.g., Weaviate, Milvus, Qdrant
    image: semitechnologies/weaviate:latest # Example
    # ... configuration and persistent volumes
  billing_service: # Optional dedicated service for complex billing logic, payment gateway interactions
    image: ai-dev-bot-billing:latest
    environment:
      # ...
      - GOOGLE_API_KEYS_JSON='[{"key": "gemini_key1_val", "active": true}, ...]' # Or path to secrets
      - OPENROUTER_API_KEYS_JSON='[{"key": "or_key1_val", "active": true}, ...]' # Or path to secrets
    # ...
    # ...
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### **Scalability Considerations**
- Horizontal scaling for **Model Orchestrator**, **Agent services/workers**, and the **Codebase Indexing Service**.
- The Vector Database for indexing needs to be scalable and performant.
- Efficient embedding generation pipelines for the Codebase Indexing Service.
- The billing and credit transaction system must be robust, reliable, and auditable.
- Regular updates to the `model_pricing` table are crucial for accurate cost calculations and profitability.

