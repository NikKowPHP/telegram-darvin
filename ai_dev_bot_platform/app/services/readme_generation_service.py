import os
from datetime import datetime
from app.core.config import settings
from typing import Dict, Any

class ReadmeGenerationService:
    def __init__(self, project_info: Dict[str, Any]):
        self.project_info = project_info
        self.current_year = datetime.now().year
        
    def generate_readme(self) -> str:
        """Generate complete README.md content"""
        sections = [
            self._generate_header(),
            self._generate_setup_instructions(),
            self._generate_configuration(),
            self._generate_usage(),
            self._generate_contributing(),
            self._generate_license()
        ]
        return "\n\n".join(filter(None, sections))
    
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

### Running the application
```bash
python -m ai_dev_bot_platform.main
```

### Running tests
```bash
pytest tests/
```"""

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