# ROO-AUDIT-TAG :: feature-008-credit-monetization.md :: Implement API endpoint for credit purchase
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Annotated
from app.services.billing_service import BillingService
from app.models.transaction import Transaction
from pydantic import BaseModel

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key")

class PurchaseRequest(BaseModel):
    package: str
    payment_token: str

@router.post("/purchase-credits", response_model=Transaction)
async def purchase_credits(
    purchase_data: PurchaseRequest,
    api_key: Annotated[str, Depends(api_key_header)],
    billing_service: BillingService = Depends()
) -> Transaction:
    """Purchase credits for the authenticated user."""
    try:
        transaction = billing_service.purchase_credits(
            api_key=api_key,
            package=purchase_data.package,
            payment_token=purchase_data.payment_token
        )
        return transaction
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
# ROO-AUDIT-TAG :: feature-008-credit-monetization.md :: END