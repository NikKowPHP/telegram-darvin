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

Create `.env` file with these variables:
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
TELEGRAM_BOT_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_api_key
{settings.ENVIRONMENT}_MODE=true
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