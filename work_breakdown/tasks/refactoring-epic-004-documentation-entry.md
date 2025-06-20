# Unify Documentation and Entry Points

## Tasks

### (LOGIC) Docker Entry Point
1. [ ] Update docker-compose command
   - Modify [`docker-compose.yml`](ai_dev_bot_platform/docker-compose.yml)
   - Change command from `uvicorn main:app` to `python run_autonomy.py`

2. [ ] Implement run_autonomy script
   - Update [`run_autonomy.py`](run_autonomy.py)
   - Add background process for Uvicorn server
   - Implement main execution loop

### (DOC) README Update
3. [ ] Rewrite execution instructions
   - Update [`README.md`](README.md)
   - Create new setup steps:
     - Set up .env
     - Run database migrations
     - Start services with run_autonomy.py
     - Explain ngrok for webhooks

4. [ ] Add architecture overview
   - Include diagram of new unified system
   - Explain role of each component