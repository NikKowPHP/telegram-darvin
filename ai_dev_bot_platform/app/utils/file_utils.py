import io
import zipfile
from typing import List, Dict


def create_project_zip(project_files: List[Dict[str, str]]) -> io.BytesIO:
    """
    Creates a ZIP file in memory from a list of project files.

    Args:
        project_files: A list of dictionaries, where each dict has "file_path" and "content".

    Returns:
        An in-memory bytes buffer containing the ZIP file.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for p_file in project_files:
            # Ensure file_path is relative and safe
            file_path = p_file.get("file_path", "unknown_file.txt")
            content = p_file.get("content", "")
            zip_file.writestr(file_path, content.encode("utf-8"))

    zip_buffer.seek(0)
    return zip_buffer
