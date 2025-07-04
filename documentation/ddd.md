# Detailed Design Document - AI-Powered Development Assistant Bot

## 5. Complete Data Dictionary
### 5.3 Table: api_key_usage
- **usage_id** (PK, UUID): Unique usage record
- **key_id** (FK): Associated API key
- **timestamp** (TIMESTAMP): Usage time
- **tokens_used** (INTEGER): Token count consumed
- **model_provider** (VARCHAR(100)): The primary source of the model. Examples: 'google', 'openrouter'.
- **model_name** (VARCHAR(255)): The unique identifier for the model. Examples: 'gemini-1.5-pro-latest', 'openrouter/anthropic/claude-3-opus', 'openrouter/google/gemini-pro' (if OpenRouter also proxies Gemini).

### 5.4 Table: conversations
- **message_id** (PK, UUID): Unique message
- **user_id** (FK): Participant user
- **content** (TEXT): Message text
- **timestamp** (TIMESTAMP): Sent time

### 5.5 Table: project_files
- **file_id** (PK, UUID): Unique file
- **project_id** (FK): Parent project
- **path** (TEXT): File path
- **content** (TEXT): File contents