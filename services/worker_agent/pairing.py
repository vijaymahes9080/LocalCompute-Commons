"""
6-Digit & QR-Based Mutual Node Pairing Protocol
"""
import time
import secrets
import hashlib
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PairingSession:
    code: str
    token_hash: str
    organization_id: Optional[str]
    created_at: float
    expires_at: float
    is_claimed: bool = False

class NodePairingEngine:
    """
    Manages secure 6-digit pairing codes for instant device onboarding.
    """
    def __init__(self, code_ttl_seconds: int = 300):
        self.code_ttl_seconds = code_ttl_seconds
        self._active_sessions: Dict[str, PairingSession] = {}

    def generate_pairing_code(self, organization_id: Optional[str] = None) -> Tuple[str, str]:
        """Generates a 6-digit pairing code and corresponding master secret token."""
        # Cryptographically secure 6-digit numeric code
        code = f"{secrets.randbelow(900000) + 100000}"
        secret_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(secret_token.encode("utf-8")).hexdigest()
        
        now = time.time()
        self._active_sessions[code] = PairingSession(
            code=code,
            token_hash=token_hash,
            organization_id=organization_id,
            created_at=now,
            expires_at=now + self.code_ttl_seconds
        )
        return code, secret_token

    def claim_pairing_code(self, code: str) -> Optional[PairingSession]:
        """Claims and consumes an active 6-digit pairing code."""
        session = self._active_sessions.get(code)
        if not session:
            return None
        if time.time() > session.expires_at or session.is_claimed:
            self._active_sessions.pop(code, None)
            return None
            
        session.is_claimed = True
        return session

pairing_engine = NodePairingEngine()
