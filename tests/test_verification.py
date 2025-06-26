import pytest
from app.services.verification_service import VerificationService
from fastapi import HTTPException

@pytest.fixture
def verification_service():
    return VerificationService()

def test_verify_implementation(verification_service):
    # Test with valid code
    result = verification_service.verify_implementation("valid code", {})
    assert isinstance(result, dict)
    assert 'valid' in result
    
    # Test error handling
    with pytest.raises(Exception):
        verification_service.verify_implementation(None, None)

def test_check_syntax(verification_service):
    assert verification_service.check_syntax("print('Hello')") is True
    assert verification_service.check_syntax("invalid code") is False

def test_validate_architecture(verification_service):
    assert verification_service.validate_architecture("file.py", {}) is True