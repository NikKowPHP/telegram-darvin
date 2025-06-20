import contextvars

# Context variable for storing current project ID
current_project_id = contextvars.ContextVar('current_project_id', default=None)

def get_current_project_id() -> str:
    """Get the current project ID from context"""
    return current_project_id.get()

def set_current_project_id(project_id: str) -> None:
    """Set the current project ID in context"""
    current_project_id.set(project_id)