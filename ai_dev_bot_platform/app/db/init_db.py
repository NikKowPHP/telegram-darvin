from app.db.session import engine, Base
from app.models.user import User
from app.models.project import Project
from app.models.project_file import ProjectFile
# Import other models as they are created
# from app.models.api_key_models import APIKey, ModelPricing, APIKeyUsage
# from app.models.transaction import CreditTransaction
# from app.models.conversation import Conversation

def init_db():
    # This will create tables if they don't exist.
    # For production, use Alembic migrations.
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized/checked.")

if __name__ == "__main__":
    init_db()