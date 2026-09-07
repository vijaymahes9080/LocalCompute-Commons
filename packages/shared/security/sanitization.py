"""
Security Sanitization, Prompt Injection Defenses, and Privacy Redaction
"""
import re
from typing import Dict, Any
from packages.shared.models.enums import PrivacyClass

# Common Prompt Injection & Jailbreak Heuristic Signatures
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s*:\s*you\s+are\s+now", re.IGNORECASE),
    re.compile(r"<\|im_start\|>", re.IGNORECASE),
    re.compile(r"<\|im_end\|>", re.IGNORECASE),
    re.compile(r"\[INST\]\s*<<SYS>>", re.IGNORECASE),
    re.compile(r"override\s+security\s+protocol", re.IGNORECASE),
    re.compile(r"bypass\s+all\s+rules", re.IGNORECASE),
]

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
IPV4_PATTERN = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
BEARER_TOKEN_PATTERN = re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE)

def sanitize_prompt_input(text: str) -> str:
    """
    Sanitizes untrusted text input to prevent delimiter injection and prompt manipulation.
    Neutralizes markdown code fence abuse and control tags.
    """
    if not text:
        return ""
    
    # Strip null bytes and control chars (except newline and tab)
    sanitized = "".join(ch for ch in text if ch == '\n' or ch == '\t' or ord(ch) >= 32)
    
    # Neutralize special chat template tokens
    sanitized = sanitized.replace("<|im_start|>", "[token:im_start]")
    sanitized = sanitized.replace("<|im_end|>", "[token:im_end]")
    sanitized = sanitized.replace("<|endoftext|>", "[token:endoftext]")
    
    return sanitized.strip()

def detect_prompt_injection(text: str) -> bool:
    """Returns True if input exhibits severe prompt injection heuristics."""
    if not text:
        return False
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(text):
            return True
    return False

def redact_sensitive_metadata(payload: Dict[str, Any], privacy_class: PrivacyClass) -> Dict[str, Any]:
    """
    Redacts sensitive identifiers, tokens, and PII from task payloads based on PrivacyClass.
    """
    if privacy_class == PrivacyClass.LOCAL_ONLY:
        # Local-only preserves full payload for local processing
        return payload

    redacted = payload.copy()
    
    # Redact common sensitive keys if present
    sensitive_keys = {"token", "auth", "secret", "password", "ip_address", "internal_ip", "authorization"}
    for key in list(redacted.keys()):
        k_lower = key.lower()
        if k_lower in sensitive_keys or any(k_lower.startswith(sens + "_") or k_lower.endswith("_" + sens) for sens in sensitive_keys):
            redacted[key] = "[REDACTED]"
            
    # If text is present, sanitize PII for STANDARD privacy
    if privacy_class == PrivacyClass.STANDARD:
        if "text" in redacted and isinstance(redacted["text"], str):
            text = redacted["text"]
            # Redact raw Bearer tokens
            text = BEARER_TOKEN_PATTERN.sub("Bearer [REDACTED_TOKEN]", text)
            redacted["text"] = text

    return redacted

def validate_document_content(text: str, max_length: int = 500_000) -> bool:
    """Strict input length and integrity validation."""
    if not text or len(text.strip()) == 0:
        return False
    if len(text) > max_length:
        return False
    return True
