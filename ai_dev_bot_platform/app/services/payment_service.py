import stripe
from typing import Optional
from app.core.config import settings
from app.schemas.user import User


class PaymentService:
    def __init__(self):
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_checkout_session(self, user: User, credit_package: str) -> Optional[str]:
        """
        Creates a Stripe Checkout Session and returns the payment URL.
        """
        # These price IDs come from your Stripe Dashboard
        price_ids = {
            "buy_100": "price_1PEXAMPLEq0j0j0j0j0j0j0j0j",
            "buy_500": "price_1PEXAMPLEr1k1k1k1k1k1k1k1k",
        }
        price_id = price_ids.get(credit_package)

        if not price_id:
            return None

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=f"{settings.WEBAPP_URL}/payment-success",
                cancel_url=f"{settings.WEBAPP_URL}/payment-cancelled",
                # IMPORTANT: This links the payment to our internal user ID
                client_reference_id=str(user.id),
            )
            return checkout_session.url
        except Exception as e:
            print(f"Error creating Stripe checkout session: {e}")
            return None
