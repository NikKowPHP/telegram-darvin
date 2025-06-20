# Complete Credit Purchase Flow

## Tasks

### (LOGIC) Payment Status Endpoints
1. [ ] Create `/payment-success` endpoint
   - Add to [`main.py`](ai_dev_bot_platform/main.py)
   - Implement GET handler with HTMLResponse

2. [ ] Create `/payment-cancelled` endpoint
   - Add to [`main.py`](ai_dev_bot_platform/main.py)
   - Implement GET handler with HTMLResponse

### (UI) HTML Responses
3. [ ] Implement success page
   - Create HTML string for successful payment
   - Include return to Telegram instructions

4. [ ] Implement cancellation page
   - Create HTML string for cancelled payment
   - Include retry purchase option

### (LOGIC) Update PaymentService
5. [ ] Modify `create_checkout_session`
   - Update [`payment_service.py`](ai_dev_bot_platform/app/services/payment_service.py)
   - Set success_url to `/payment-success`
   - Set cancel_url to `/payment-cancelled`