# ROO-AUDIT-TAG :: feature-008-credit-monetization.md :: Implement API call cost tracking
from typing import Optional
from fastapi import HTTPException, status
from app.db.session import SessionLocal
from app.models.api_key_models import APIKey
from app.models.user import User
from app.schemas.api_key_schemas import APIKeyUsage

class APIKeyManager:
    """Service for managing API key authentication and credit tracking."""
    
    def __init__(self):
        self.credit_costs = {
            "conversation": 1,
            "code_generation": 3,
            "documentation": 2,
            "search": 1
        }
        
    def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate an API key and return its associated user."""
        db = SessionLocal()
        try:
            key = db.query(APIKey).filter(APIKey.key == api_key).first()
            if not key or not key.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or inactive API key"
                )
            return key
        finally:
            db.close()
            
    def track_usage(self, api_key: str, operation: str) -> APIKeyUsage:
        """Track API usage and deduct appropriate credits."""
        # ROO-AUDIT-TAG :: feature-008-credit-monetization.md :: Credit deduction logic
        db = SessionLocal()
        try:
            key = self.validate_api_key(api_key)
            user = db.query(User).get(key.user_id)
            
            cost = self.credit_costs.get(operation, 1)
            if user.credit_balance < cost:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Insufficient credits"
                )
                
            user.credit_balance -= cost
            db.commit()
            
            return APIKeyUsage(
                user_id=user.id,
                operation=operation,
                cost=cost,
                remaining_credits=user.credit_balance
            )
        finally:
            db.close()
# ROO-AUDIT-TAG :: feature-008-credit-monetization.md :: END