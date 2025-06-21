# Epic 2: Implement Persistent Codebase Indexing

- [ ] (IMPLEMENT) Execute existing refactor plan from documentation: `documentation/scaling_on_raspberry.md`
- [ ] (DB) Generate and apply pgvector database migration: Run `alembic revision --autogenerate -m "Add project_embeddings table for pgvector"` and `alembic upgrade head`