from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from app.api.deps import get_db, get_current_active_user, get_current_active_admin
from app.schemas.user import User
from app.schemas.transaction import CreditTransactionCreate
from app.services.billing_service import CreditTransactionService

router = APIRouter()

@router.post("/admin/set-credits")
async def admin_set_user_credits(
    user_id: int,
    amount: Decimal,
    description: str,
    db: Session = Depends(get_db),
    admin_user: User = Security(get_current_active_admin, scopes=["admin"]),
):
    """
    ADMIN ENDPOINT: Set a user's credit balance directly.
    Requires admin privileges.
    """
    try:
        billing_service = CreditTransactionService()
        
        # First clear any existing balance by creating a zeroing transaction
        current_balance = billing_service.get_user_balance(db, user_id)
        if current_balance != 0:
            await billing_service.record_transaction(
                db,
                CreditTransactionCreate(
                    user_id=user_id,
                    transaction_type="admin_adjustment",
                    credits_amount=-current_balance,
                    description=f"Zeroing balance for admin adjustment"
                )
            )
        
        # Then set the new balance
        transaction = await billing_service.record_transaction(
            db,
            CreditTransactionCreate(
                user_id=user_id,
                transaction_type="admin_adjustment",
                credits_amount=amount,
                description=description
            )
        )
        
        return {
            "status": "success",
            "user_id": user_id,
            "new_balance": billing_service.get_user_balance(db, user_id),
            "transaction_id": transaction.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to set credits: {str(e)}"
        )

@router.get("/balance")
async def get_user_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current credit balance for authenticated user"""
    try:
        billing_service = CreditTransactionService()
        balance = billing_service.get_user_balance(db, current_user.id)
        return {"user_id": current_user.id, "balance": balance}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get balance: {str(e)}"
        )

@router.get("/transactions")
async def get_user_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get transaction history for authenticated user"""
    try:
        billing_service = CreditTransactionService()
        transactions = billing_service.get_transactions_for_user(db, current_user.id)
        return {
            "user_id": current_user.id,
            "transactions": transactions,
            "count": len(transactions)
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get transactions: {str(e)}"
        )