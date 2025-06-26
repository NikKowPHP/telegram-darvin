import pytest
from app.services.codebase_indexing_service import CodebaseIndexingService

@pytest.fixture
def indexing_service():
    return CodebaseIndexingService()

def test_index_codebase(indexing_service):
    """Test indexing a collection of code files."""
    test_files = [
        {'path': 'file1.py', 'content': 'def foo(): pass'},
        {'path': 'file2.py', 'content': 'class Bar: pass'}
    ]
    
    indexing_service.index_codebase(test_files)
    
    assert len(indexing_service.code_vectors) == 2
    assert len(indexing_service.code_metadata) == 2
    assert indexing_service.index.ntotal == 2

def test_search_codebase(indexing_service):
    """Test searching the indexed codebase."""
    test_files = [
        {'path': 'file1.py', 'content': 'def foo(): pass'},
        {'path': 'file2.py', 'content': 'class Bar: pass'}
    ]
    indexing_service.index_codebase(test_files)
    
    results = indexing_service.search_codebase('foo', k=1)
    
    assert len(results) == 1
    assert results[0]['file'] == 'file1.py'

def test_update_index(indexing_service):
    """Test updating an existing file in the index."""
    test_files = [{'path': 'file1.py', 'content': 'def foo(): pass'}]
    indexing_service.index_codebase(test_files)
    
    # Update the file content
    indexing_service.update_index('file1.py', 'def foo(): return 42')
    
    results = indexing_service.search_codebase('return', k=1)
    assert len(results) == 1
    assert 'return 42' in results[0]['content']

def test_empty_code(indexing_service):
    """Test handling empty code files."""
    test_files = [{'path': 'empty.py', 'content': ''}]
    indexing_service.index_codebase(test_files)
    
    assert len(indexing_service.code_vectors) == 1