Of course. Based on the detailed analysis and the defined path forward, I will create a new, comprehensive `implementation_todo.md` file.

This plan is meticulously structured for a small, autonomous 4B LLM agent. It breaks down the complex task of integrating a payment provider into simple, sequential, and explicit steps. Each task is an atomic unit of work with clear verification criteria to ensure a successful and robust implementation.

---
Here is the content for the new file:

# `implementation_todo.md` - Live Payments and Advanced Logic

**Project Goal:** To implement a production-grade, toggleable Stripe payment system, add advanced orchestration logic for handling insufficient credits, and expand the test suite to cover these new, critical features.

**Guiding Principle:** Complete each task in the exact order it is presented. Verify each step before proceeding to the next.

---

## Feature 1: Configuration for Toggleable Payments

**Goal:** Update the project's configuration to support a "mock" mode for Stripe payments and to store necessary URLs.

*   `[x]` **F1.1: Add new environment variables for Stripe and Mocking**
    *   **File:** `ai_dev_bot_platform/.env.example`
    *   **Action:** Add the following variables to the end of the file.
        ```env
        # Set to 'true' to simulate successful payments without calling Stripe
        MOCK_STRIPE_PAYMENTS=true

        # Stripe Publishable Key (safe to expose in client-side code)
        STRIPE_PUBLISHABLE_KEY="pk_test_YOUR_KEY"

        # The base URL of your web application for Stripe redirects
        WEBAPP_URL=http://localhost:8000
        ```
    *   **File:** `ai_dev_bot_platform/app/core/config.py`
    *   **Action:** Add the corresponding variables to the `Settings` class.
        ```python
        # In the Settings class, after the other Stripe variables
        MOCK_STRIPE_PAYMENTS: bool = False
        STRIPE_PUBLISHABLE_KEY: Optional[str] = None
        WEBAPP_URL: str = "http://localhost:8000"
        ```
    *   **Verification:** The new variables are present in both the example environment file and the Pydantic `Settings` class.

---

## Feature 2: Full Stripe Integration (Live and Mock)

**Goal:** Build the services and API endpoints required to create Stripe Checkout sessions and handle incoming webhooks.

*   `[x]` **F2.1: Create a dedicated Payment Service**
    *   **File:** `ai_dev_bot_platform/app/services/payment_service.py` (Create this new file)
    *   **Action:** Add the following content. This service will be responsible for all interactions with the Stripe API.
        ```python
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
                    'buy_100': 'price_1PEXAMPLEq0j0j0j0j0j0j0j0j',
                    'buy_500': 'price_1PEXAMPLEr1k1k1k1k1k1k1k1k',
                }
                price_id = price_ids.get(credit_package)

                if not price_id:
                    return None

                try:
                    checkout_session = stripe.checkout.Session.create(
                        line_items=[
                            {
                                'price': price_id,
                                'quantity': 1,
                            },
                        ],
                        mode='payment',
                        success_url=f"{settings.WEBAPP_URL}/payment-success",
                        cancel_url=f"{settings.WEBAPP_URL}/payment-cancelled",
                        # IMPORTANT: This links the payment to our internal user ID
                        client_reference_id=str(user.id),
                    )
                    return checkout_session.url
                except Exception as e:
                    print(f"Error creating Stripe checkout session: {e}")
                    return None
        ```
    *   **Verification:** The file `app/services/payment_service.py` exists and contains the `PaymentService` class.

*   `[ ]` **F2.2: Create the Stripe Webhook API Endpoint**
    *   **File:** `ai_dev_bot_platform/app/api/endpoints/stripe_webhooks.py` (Create the `api/endpoints` directories first)
    *   **Action:** Add the following content to the new file. This endpoint will listen for events from Stripe.
        ```python
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
        ```
    *   **Verification:** The `stripe_webhooks.py` file exists and contains the webhook router and logic.

*   `[ ]` **F2.3: Mount the new webhook router in the main application**
    *   **File:** `ai_dev_bot_platform/main.py`
    *   **Action:**
        1.  Add the import: `from app.api.endpoints import stripe_webhooks`.
        2.  After the `app = FastAPI(...)` line, add the following line to include the new router:
            ```python
            app.include_router(stripe_webhooks.router, prefix="/api/v1", tags=["Stripe"])
            ```
    *   **Verification:** `main.py` now mounts the Stripe webhook router.

*   `[ ]` **F2.4: Update the Telegram button handler to use the new payment flow**
    *   **File:** `ai_dev_bot_platform/app/telegram_bot/handlers.py`
    *   **Action:**
        1.  Add the imports: `from app.services.payment_service import PaymentService` and `from app.core.config import settings`.
        2.  Replace the entire `button_handler` function with this new implementation that supports both mock and live modes.
            ```python
            async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
                query = update.callback_query
                await query.answer()
                
                user_tg = update.effective_user
                credit_package = query.data

                db: Session = SessionLocal()
                try:
                    user_service = UserService()
                    user_db = user_service.get_user_by_telegram_id(db, user_tg.id)
                    if not user_db:
                        await query.edit_message_text(text="Could not find your account. Please /start first.")
                        return

                    if settings.MOCK_STRIPE_PAYMENTS:
                        # MOCK FLOW: Directly add credits
                        updated_user = user_service.add_credits_after_purchase(db, user_id=user_db.id, credit_package=credit_package)
                        if updated_user:
                            await query.edit_message_text(
                                text=f"Success! Your MOCK purchase was processed. "
                                     f"New balance: {updated_user.credit_balance:.2f}"
                            )
                        else:
                            await query.edit_message_text(text="An error occurred during the mock purchase.")
                    else:
                        # LIVE FLOW: Generate a Stripe Checkout link
                        payment_service = PaymentService()
                        checkout_url = payment_service.create_checkout_session(user=user_db, credit_package=credit_package)
                        
                        if checkout_url:
                            keyboard = [[InlineKeyboardButton("➡️ Proceed to Payment", url=checkout_url)]]
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            await query.edit_message_text(
                                text="Please complete your purchase using the link below:",
                                reply_markup=reply_markup
                            )
                        else:
                            await query.edit_message_text(text="Sorry, we could not create a payment link at this time.")
                
                except Exception as e:
                    logger.error(f"Error in button_handler: {e}", exc_info=True)
                    await query.edit_message_text(text="A server error occurred. Please try again later.")
                finally:
                    db.close()
            ```
    *   **Verification:** Clicking the credit buttons now sends a Stripe payment link when `MOCK_STRIPE_PAYMENTS` is false, and simulates the purchase when it is true.

---

## Feature 3: Documentation Update for Stripe

**Goal:** Update the main `README.md` to explain the new Stripe variables and how to test webhooks locally.

*   `[ ]` **F3.1: Update README.md with Stripe and Webhook instructions**
    *   **File:** `README.md`
    *   **Action:** Find the `### Running with a Proxy` section. Add a new section directly below it titled `### Testing Stripe Webhooks Locally`.
        ```markdown
        ### Testing Stripe Webhooks Locally

        To test the full payment flow with Stripe, you need a way for Stripe's servers to send events to your local machine. We use `ngrok` for this.

        1.  **Install `ngrok`:** Follow the instructions on the [ngrok website](https://ngrok.com/download).

        2.  **Run `ngrok`:** In a separate terminal, start `ngrok` to expose your local port 8000 to the internet.
            ```bash
            ngrok http 8000
            ```

        3.  **Get Your Webhook URL:** `ngrok` will give you a public URL (e.g., `https://random-string.ngrok.io`). Your full webhook URL will be this URL plus the API path:
            `https://random-string.ngrok.io/api/v1/stripe-webhook`

        4.  **Configure Stripe:** Go to your Stripe Dashboard, navigate to the "Webhooks" section, and add a new endpoint. Paste the full URL from the previous step. For the events, select "Listen to all events" for now, or specifically `checkout.session.completed`.

        5.  **Set `MOCK_STRIPE_PAYMENTS` to `false`** in your `.env` file to enable the live Stripe flow. Now, when you click a "Buy Credits" button, you will be redirected to a real Stripe checkout page. After a successful payment, Stripe will send an event to your `ngrok` URL, which will forward it to your local application to grant the credits.
        ```
    *   **Verification:** The `README.md` file now contains the detailed instructions for testing Stripe webhooks locally.