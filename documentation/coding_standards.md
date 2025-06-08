# Coding Standards - AI-Powered Development Assistant

## 1. Naming Conventions
### Variables
- `snake_case` for all variables
- Descriptive names: `user_credits` not `uc`

### Functions
- `snake_case` with verb-noun structure
- `generate_python_code()` not `genPyCode()`

### Classes
- `PascalCase` with descriptive names
- `CodeGenerator` not `CG`

## 2. Code Formatting
- Line length: 88 characters (Black compatible)
- Indentation: 4 spaces
- Imports: grouped as stdlib, third-party, local

## 3. Error Handling
### Exceptions
- Use built-in exceptions when appropriate
- Create custom exceptions for domain-specific errors
```python
class CreditDeductionError(Exception):
    """Raised when credit transactions fail"""
```

### Logging
- Use structured logging with context
```python
logger.error(
    "LLM API failed", 
    extra={"user": user_id, "endpoint": api_url}
)
```

## 4. LLM Best Practices
- Validate all LLM outputs with schemas
- Implement exponential backoff for API calls
- Sanitize prompts to prevent injection attacks

## 5. Security
- Never hardcode API keys - use environment variables
- Use parameterized queries for database access
- Validate all user inputs with strict schemas