"""
Unit Tests for Authentication, Token Creation, and RBAC
"""
import pytest
from packages.shared.models.enums import UserRole
from packages.shared.security.auth import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token,
    create_node_token, decode_token
)

def test_password_hashing():
    raw = "SuperSecretPassword2026!"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_jwt_access_and_refresh_tokens():
    payload = {"sub": "testuser", "role": UserRole.USER.value}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    
    decoded_access = decode_token(access_token)
    assert decoded_access["sub"] == "testuser"
    assert decoded_access["type"] == "access"
    assert decoded_access["role"] == "user"

    decoded_refresh = decode_token(refresh_token)
    assert decoded_refresh["sub"] == "testuser"
    assert decoded_refresh["type"] == "refresh"

def test_worker_node_token():
    node_id = "node-alpha-100"
    node_token = create_node_token(node_id, org_id="org-1")
    
    decoded = decode_token(node_token)
    assert decoded["sub"] == node_id
    assert decoded["node_id"] == node_id
    assert decoded["type"] == "worker"
