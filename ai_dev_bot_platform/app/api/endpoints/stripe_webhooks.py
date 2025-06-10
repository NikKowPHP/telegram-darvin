import stripe
import logging
from fastapi import APIRouter, Request, Header
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=stripe_signature, secret=settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Stripe webhook value error: {e}")
        return {"status": "invalid payload"}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Stripe webhook signature error: {e}")
        return {"status": "invalid signature"}, 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id_str = session.get('client_reference_id')
        
        if not user_id_str:
            logger.error("Webhook received without client_reference_id")
            return {"status": "error", "message": "Missing client_reference_id"}, 400

        # This is a simplification. A real app would look up the line items
        # to determine exactly what was purchased.
        credit_package_key = session['display_items'][0]['custom']['name'].lower().replace(' ', '_')

        db: Session = SessionLocal()
        try:
            user_service = UserService()
            user_service.add_credits_after_purchase(
                db=db, 
                user_id=int(user_id_str), 
                credit_package=credit_package_key
            )
            logger.info(f"Successfully processed purchase for user {user_id_str}")
        finally:
            db.close()

    return {"status": "success"}