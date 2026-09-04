import pytest
from fastapi import HTTPException
from app.security import validate_public_url

def test_rejects_unsupported_protocol():
    with pytest.raises(HTTPException): validate_public_url('ftp://example.com/file')
def test_rejects_localhost():
    with pytest.raises(HTTPException): validate_public_url('http://localhost:8000')
