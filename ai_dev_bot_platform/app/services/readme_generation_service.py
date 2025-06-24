import os
from datetime import datetime
from app.core.config import settings
from typing import Dict, Any


class ReadmeGenerationService:
    def __init__(self, project_info: Dict[str, Any]):
        self.project_info = project_info
        self.current_year = datetime.now().year

    def generate_readme(self, format: str = "markdown") -> str:
        """Generate complete README content in specified format"""
        if format not in ["markdown", "html", "rst"]:
            raise ValueError(f"Unsupported format: {format}")

        sections = [
            self._generate_header(),
            self._generate_badges(),
            self._generate_setup_instructions(),
            self._generate_configuration(),
            self._generate_usage(),
            self._generate_api_docs(),
            self._generate_contributing(),
            self._generate_license(),
        ]

        content = "\n\n".join(filter(None, sections))

        if format == "html":
            from markdown import markdown

            content = markdown(content)
        elif format == "rst":
            from m2r import convert

            content = convert(content)

        return content

    def _generate_badges(self) -> str:
        """Generate status badges for the project"""
        badges = []
        if self.project_info.get("ci_url"):
            badges.append(
                f"[![CI Status]({self.project_info['ci_url']}/badge.svg)]"
                f"({self.project_info['ci_url']})"
            )
        if self.project_info.get("coverage_url"):
            badges.append(
                f"[![Coverage]({self.project_info['coverage_url']}/badge.svg)]"
                f"({self.project_info['coverage_url']})"
            )
        if self.project_info.get("pypi_version"):
            badges.append(
                f"[![PyPI Version](https://img.shields.io/pypi/v/"
                f"{self.project_info['name']}.svg)]"
                f"(https://pypi.org/project/{self.project_info['name']}/)"
            )

        return "\n".join(badges) + "\n" if badges else ""

    def _generate_api_docs(self) -> str:
        """Generate API documentation section"""
        if not self.project_info.get("api_docs"):
            return ""

        return f"""## API Documentation

The following API endpoints are available:

{self._format_endpoints(self.project_info['api_docs'])}

For interactive documentation, visit:
- Swagger UI: {self.project_info.get('swagger_url', '/docs')}
- ReDoc: {self.project_info.get('redoc_url', '/redoc')}"""

    def _format_endpoints(self, endpoints: list) -> str:
        """Format API endpoints as a markdown table"""
        if not endpoints:
            return ""

        table = "| Method | Path | Description |\n"
        table += "|--------|------|-------------|\n"
        for endpoint in endpoints:
            table += f"| {endpoint.get('method', 'GET')} "
            table += f"| `{endpoint.get('path', '')}` "
            table += f"| {endpoint.get('description', '')} |\n"
        return table

    def _generate_header(self) -> str:
        return f"""# {self.project_info.get('name', 'Project Name')}

{self.project_info.get('description', 'Project description')}"""

    def _generate_setup_instructions(self) -> str:
        return """## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ (with createdb privileges)
- Redis 6.2+
- Git

### Database Setup
1. Create PostgreSQL database and user:
   ```bash
   sudo -u postgres psql -c "CREATE USER ai_dev_bot WITH PASSWORD 'securepassword';"
   sudo -u postgres psql -c "CREATE DATABASE ai_dev_bot WITH OWNER ai_dev_bot;"
   ```

### Redis Setup
1. Install and start Redis server:
   ```bash
   sudo apt install redis-server
   sudo systemctl enable redis-server
   sudo systemctl start redis-server
   ```

### Application Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-dev-bot-platform.git
   cd ai-dev-bot-platform
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run database migrations:
   ```bash
   alembic upgrade head
   ```
5. Set up environment variables (see Configuration section)

### Verification
1. Run tests to verify installation:
   ```bash
   pytest tests/
   ```
2. Start development server:
   ```bash
   python -m ai_dev_bot_platform.main
   ```"""

    def _generate_configuration(self) -> str:
        return f"""## ⚙️ Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory with these settings:

### Core Settings
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development  # or 'production'
```

### Telegram Integration
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_ID=your_admin_user_id
```

### AI Services
```
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_REFERRER=your_project_name
GOOGLE_API_KEY=your_google_api_key  # Optional for some features
```

### Security & Rate Limiting
```
JWT_SECRET_KEY=your_jwt_secret_key
API_RATE_LIMIT=100  # Requests per minute per user
```

### Monitoring & Analytics
```
SENTRY_DSN=your_sentry_dsn  # Optional error tracking
GOOGLE_ANALYTICS_ID=UA-XXXXX-Y  # Optional analytics
```

### Email/SMTP Settings (Optional)
```
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=user@example.com
SMTP_PASSWORD=your_email_password
EMAIL_FROM=no-reply@example.com
```"""

    def _generate_usage(self) -> str:
        return """## 💻 Usage

### Development Mode
```bash
# Start the development server with auto-reload
uvicorn ai_dev_bot_platform.main:app --reload --port 8000
```

### Production Mode
```bash
# Build production Docker image
docker build -t ai-dev-bot-platform .

# Run the production container
docker run -d --name ai-dev-bot \
  -p 8000:8000 \
  -v ./data:/app/data \
  --env-file .env \
  ai-dev-bot-platform
```

### Common Operations
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_user_model.py

# Start background worker for async tasks
celery -A ai_dev_bot_platform.worker worker --loglevel=info

# Database migrations
alembic upgrade head  # Apply migrations
alembic revision --autogenerate -m "description"  # Create new migration
```

### API Documentation
After starting the server, access these endpoints:
- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json"""

    def _generate_contributing(self) -> str:
        return """## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request"""

    def _generate_license(self) -> str:
        return f"""## 📄 License

Copyright {self.current_year} - Present, Your Name. All rights reserved."""
