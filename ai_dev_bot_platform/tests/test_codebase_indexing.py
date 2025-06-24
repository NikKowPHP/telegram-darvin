import pytest
import asyncio
from unittest.mock import MagicMock, patch
from app.services.codebase_indexing_service import CodebaseIndexingService
from app.services.api_key_manager import APIKeyManager


@pytest.mark.asyncio
async def test_indexing_service_integration():
    """Test the integration of the indexing service with other components."""
    # Setup
    api_key_manager = MagicMock(spec=APIKeyManager)
    indexing_service = CodebaseIndexingService(api_key_manager)

    # Mock the LLM client
    with patch.object(indexing_service, "llm_client", autospec=True) as mock_llm:
        # Mock the LLM response
        mock_llm.generate_response.return_value = {
            "choices": [{"message": {"content": "Indexed content"}}]
        }

        # Test indexing a file
        result = await indexing_service.index_file_content(
            project_id="test_project",
            file_path="src/main.py",
            content="print('Hello, world!')",
        )

        # Verify the LLM was called with the correct parameters
        mock_llm.generate_response.assert_called_once()
        call_args = mock_llm.generate_response.call_args[0][0]
        assert "src/main.py" in call_args["prompt"]
        assert "print('Hello, world!')" in call_args["prompt"]

        # Verify the result
        assert result is not None
        assert "Indexed content" in result


@pytest.mark.asyncio
async def test_search_functionality():
    """Test the search functionality across the codebase."""
    # Setup
    api_key_manager = MagicMock(spec=APIKeyManager)
    indexing_service = CodebaseIndexingService(api_key_manager)

    # Mock the LLM client
    with patch.object(indexing_service, "llm_client", autospec=True) as mock_llm:
        # Mock the LLM response with search results
        mock_llm.generate_response.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "File: src/main.py\nLine 10: print('Hello, world!')"
                    }
                }
            ]
        }

        # Test searching the codebase
        results = await indexing_service.query_codebase(
            project_id="test_project", query="print('Hello'"
        )

        # Verify the LLM was called with the correct parameters
        mock_llm.generate_response.assert_called_once()
        call_args = mock_llm.generate_response.call_args[0][0]
        assert "print('Hello'" in call_args["prompt"]

        # Verify the results
        assert len(results) == 1
        assert "src/main.py" in results[0]["file_path"]
        assert "print('Hello, world!')" in results[0]["content"]


@pytest.mark.asyncio
async def test_context_preservation():
    """Test that context is preserved in search results."""
    # Setup
    api_key_manager = MagicMock(spec=APIKeyManager)
    indexing_service = CodebaseIndexingService(api_key_manager)

    # Mock the LLM client
    with patch.object(indexing_service, "llm_client", autospec=True) as mock_llm:
        # Mock the LLM response with context
        mock_llm.generate_response.return_value = {
            "choices": [
                {
                    "message": {
                        "content": (
                            "File: src/utils.py\n"
                            "Line 5: def format_date(date):\n"
                            "Line 6:    return date.strftime('%Y-%m-%d')\n"
                            "Line 7: def add(a, b):\n"
                            "Line 8:    return a + b"
                        )
                    }
                }
            ]
        }

        # Test searching with context preservation
        results = await indexing_service.query_codebase(
            project_id="test_project", query="format_date"
        )

        # Verify the results include proper context
        assert len(results) == 1
        assert "src/utils.py" in results[0]["file_path"]
        assert "def format_date(date):" in results[0]["content"]
        assert "def add(a, b):" in results[0]["content"]
        assert results[0]["content"].count("\n") >= 2  # Multiple lines of context


@pytest.mark.asyncio
async def test_integration_with_storage():
    """Test the integration between indexing service and storage service."""
    # Setup
    api_key_manager = MagicMock(spec=APIKeyManager)
    indexing_service = CodebaseIndexingService(api_key_manager)

    # Mock the storage service
    with patch.object(
        indexing_service, "storage_service", autospec=True
    ) as mock_storage:
        # Mock downloading a file
        mock_storage.download_file.return_value = "print('Hello, world!')"

        # Mock the LLM client
        with patch.object(indexing_service, "llm_client", autospec=True) as mock_llm:
            mock_llm.generate_response.return_value = {
                "choices": [{"message": {"content": "Indexed content"}}]
            }

            # Test indexing a file from storage
            result = await indexing_service.index_file_from_storage(
                project_id="test_project", file_path="src/main.py"
            )

            # Verify storage was called
            mock_storage.download_file.assert_called_once_with(
                bucket_name="test_project", file_path="src/main.py"
            )

            # Verify indexing was performed
            mock_llm.generate_response.assert_called_once()
            assert result is not None
            assert "Indexed content" in result
