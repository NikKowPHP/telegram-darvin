app-1    | 2025-06-13 12:01:32,074 - app.services.orchestrator_service - ERROR - No pricing found for model openrouter/deepseek/deepseek-r1-0528:free. Cannot deduct credits for user 1.
app-1    | 2025-06-13 12:01:33,199 - httpx - INFO - HTTP Request: POST https://api.telegram.org/bot8015987158:AAGNYmx7WSssHRHSd8MdcsYkZq6GGImo5uM/sendMessage "HTTP/1.1 200 OK"

if no pricing then we should charge for resource usage

resilience to the api calls from models