from sqlalchemy.orm import Session
from app.models.api_key_models import ModelPricing
from app.schemas.api_key_schemas import ModelPricingCreate, ModelPricingUpdate
from typing import Optional, List

class ModelPricingService:
    def get_pricing(self, db: Session, model_provider: str, model_name: str) -> Optional[ModelPricing]:
        return db.query(ModelPricing).filter(
            ModelPricing.model_provider == model_provider,
            ModelPricing.model_name == model_name,
            ModelPricing.is_active == True
        ).first()

    def create_pricing(self, db: Session, pricing_in: ModelPricingCreate) -> ModelPricing:
        db_pricing = ModelPricing(**pricing_in.model_dump())
        db.add(db_pricing)
        db.commit()
        db.refresh(db_pricing)
        return db_pricing
    
    def update_pricing(self, db: Session, pricing_id: int, pricing_in: ModelPricingUpdate) -> Optional[ModelPricing]:
        db_pricing = db.query(ModelPricing).filter(ModelPricing.id == pricing_id).first()
        if not db_pricing:
            return None
            
        update_data = pricing_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_pricing, field, value)
            
        db.add(db_pricing)
        db.commit()
        db.refresh(db_pricing)
        return db_pricing
        
    def list_active_pricings(self, db: Session) -> List[ModelPricing]:
        return db.query(ModelPricing).filter(ModelPricing.is_active == True).all()

class APIKeyUsageService:
    def log_usage(self, db: Session, usage_in: APIKeyUsageCreate) -> APIKeyUsage:
        db_usage = APIKeyUsage(**usage_in.model_dump())
        db.add(db_usage)
        db.commit()
        db.refresh(db_usage)
        return db_usage

    def get_usage_by_project(self, db: Session, project_id: uuid.UUID) -> List[APIKeyUsage]:
        return db.query(APIKeyUsage).filter(APIKeyUsage.project_id == project_id).all()

    def get_usage_by_user(self, db: Session, user_id: int) -> List[APIKeyUsage]:
        return db.query(APIKeyUsage).filter(APIKeyUsage.user_id == user_id).all()