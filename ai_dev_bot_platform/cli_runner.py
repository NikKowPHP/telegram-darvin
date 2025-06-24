import argparse
import uuid
import json
from typing import Optional
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.project_helpers import get_project_helpers
from app.services.user_service import UserService
from app.schemas.user import User


def main():
    parser = argparse.ArgumentParser(description="Roo Agent CLI Interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Generate plan command
    plan_parser = subparsers.add_parser("generate-plan")
    plan_parser.add_argument("--project-id", required=True)
    plan_parser.add_argument("--description", required=True)

    # Implement task command
    task_parser = subparsers.add_parser("implement-task")
    task_parser.add_argument("--project-id", required=True)
    task_parser.add_argument("--task", required=True)

    # Deduct credits command
    credits_parser = subparsers.add_parser("deduct-credits")
    credits_parser.add_argument("--user-id", required=True)
    credits_parser.add_argument("--input-tokens", type=int, required=True)
    credits_parser.add_argument("--output-tokens", type=int, required=True)
    credits_parser.add_argument("--model-name", required=True)
    credits_parser.add_argument("--task-type", required=True)
    credits_parser.add_argument("--project-id", required=False)

    args = parser.parse_args()

    db: Session = SessionLocal()
    try:
        if args.command == "generate-plan":
            handle_generate_plan(db, args.project_id, args.description)
        elif args.command == "implement-task":
            handle_implement_task(db, args.project_id, args.task)
        elif args.command == "deduct-credits":
            handle_deduct_credits(db, args)
    finally:
        db.close()


def handle_generate_plan(db: Session, project_id: str, description: str):
    """Handle generate plan command"""
    helpers = get_project_helpers(db)
    user_service = UserService()

    # In a real implementation, we would get the user from the project
    # For now, just demonstrate the CLI structure
    print(f"Generating plan for project {project_id}")
    print(f"Description: {description}")


def handle_implement_task(db: Session, project_id: str, task: str):
    """Handle implement task command"""
    helpers = get_project_helpers(db)
    print(f"Implementing task for project {project_id}")
    print(f"Task: {task}")


def handle_deduct_credits(db: Session, args):
    """Handle deduct credits command"""
    helpers = get_project_helpers(db)
    user_service = UserService()
    user = user_service.get_user_by_id(db, int(args.user_id))

    if not user:
        print(f"Error: User {args.user_id} not found")
        return

    llm_data = {
        "model_name_used": args.model_name,
        "input_tokens": args.input_tokens,
        "output_tokens": args.output_tokens,
    }

    project_id = uuid.UUID(args.project_id) if args.project_id else None
    helpers.deduct_credits_for_llm_call(
        user=user,
        llm_response_data=llm_data,
        task_type=args.task_type,
        project_id=project_id,
    )
    print(f"Deducted credits for user {user.id}")


if __name__ == "__main__":
    main()
