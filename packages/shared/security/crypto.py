"""
Cryptographic integrity, hash chaining, and result signing
"""
import hashlib
import hmac
import json
from typing import Dict, Any

def compute_sha256(content: str) -> str:
    """Computes SHA-256 hex digest of string content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def compute_payload_checksum(payload: Dict[str, Any]) -> str:
    """Computes canonical deterministic JSON SHA-256 checksum."""
    serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def generate_task_signature(task_id: str, output_payload: Dict[str, Any], secret: str) -> str:
    """Generates HMAC-SHA256 signature for task results."""
    serialized = json.dumps(output_payload, sort_keys=True, separators=(',', ':'))
    message = f"{task_id}:{serialized}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()

def verify_task_signature(task_id: str, output_payload: Dict[str, Any], signature: str, secret: str) -> bool:
    """Verifies HMAC-SHA256 signature for task results."""
    expected = generate_task_signature(task_id, output_payload, secret)
    return hmac.compare_digest(expected, signature)

def compute_audit_event_hash(
    event_type: str,
    actor_id: str,
    target_id: str,
    timestamp: str,
    details: Dict[str, Any]
) -> str:
    """Computes tamper-evident hash for audit events."""
    raw = f"{event_type}|{actor_id}|{target_id}|{timestamp}|{json.dumps(details, sort_keys=True)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
