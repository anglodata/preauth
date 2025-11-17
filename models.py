"""
Data models for credentials and records.
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Credential:
    """Registered WebAuthn credential."""
    id: str
    public_key_pem: str
    sign_count: int

@dataclass
class UserRecord:
    """Participant record with optional TOTP secret."""
    email: str
    totp_secret: Optional[str] = None

@dataclass
class AdminRecord:
    """Admin record with WebAuthn credentials."""
    admin_id: str
    credentials: List[Credential]
