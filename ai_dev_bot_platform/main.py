from fastapi import FastAPI
from app.core.logging_config import setup_logging

app = FastAPI(title="AI Development Assistant API")

setup_logging()

@app.get("/")
async def root():
    return {"message": "AI Development Assistant API is running!"}

# Placeholder for future app setup
# def create_application() -> FastAPI:
#     application = FastAPI()
#     # ... add routers, middleware, etc.
#     return application
#
# app = create_application()