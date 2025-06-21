# Epic 5: Resolve Audit Failures

### 1. Add Missing Implementation Tags
- [ ] (AUDIT) Add ROO-AUDIT-TAG to [`architect_agent.py`](ai_dev_bot_platform/app/agents/architect_agent.py) for task `plan-003-architect-agent.md`
- [ ] (AUDIT) Add ROO-AUDIT-TAG to [`codebase_indexing_service.py`](ai_dev_bot_platform/app/services/codebase_indexing_service.py) for task `plan-004-codebase-indexing.md`
- [ ] (AUDIT) Add ROO-AUDIT-TAG to [`implementer_agent.py`](ai_dev_bot_platform/app/agents/implementer_agent.py) for task `plan-005-implementer-agent.md`
- [ ] (AUDIT) Add ROO-AUDIT-TAG to [`readme_generation_service.py`](ai_dev_bot_platform/app/services/readme_generation_service.py) for task `plan-007-readme-generator.md`
- [ ] (AUDIT) Add ROO-AUDIT-TAG to [`billing_service.py`](ai_dev_bot_platform/app/services/billing_service.py) for task `plan-008-credit-management.md`
- [ ] (AUDIT) Add ROO-AUDIT-TAG to [`payment_service.py`](ai_dev_bot_platform/app/services/payment_service.py) for task `plan-008-credit-management.md`

### 2. Complete Partial Tagging
- [ ] (AUDIT) Add ROO-AUDIT-TAG to [`cli_runner.py`](ai_dev_bot_platform/cli_runner.py) for task `refactoring-epic-001-architectural-conflict.md`
- [ ] (AUDIT) Add ROO-AUDIT-TAG to [`project_helpers.py`](ai_dev_bot_platform/app/services/project_helpers.py) for task `refactoring-epic-001-architectural-conflict.md`

### 3. Complete Missing Implementations
- [ ] (LOGIC) Implement payment status endpoints in [`main.py`](ai_dev_bot_platform/main.py) for task `refactoring-epic-003-credit-purchase.md`
- [ ] (UI) Create HTML responses for payment status in [`main.py`](ai_dev_bot_platform/main.py) for task `refactoring-epic-003-credit-purchase.md`
- [ ] (AUDIT) Add ROO-AUDIT-TAG to payment status implementation in [`main.py`](ai_dev_bot_platform/main.py)
- [ ] (CONFIG) Update CMD in [`docker-compose.yml`](ai_dev_bot_platform/docker-compose.yml) to use `run_autonomy.py`
- [ ] (CONFIG) Update CMD in [`docker-compose.prod.yml`](deploy/docker/docker-compose.prod.yml) to use `run_autonomy.py`
- [ ] (AUDIT) Add ROO-AUDIT-TAG to Docker Compose updates