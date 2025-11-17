"""
WebAuthn service wrapping python-fido2 for registration/login.
Forces platform authenticator and user verification.
"""

import base64
import logging
from typing import Dict, Any
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity

from config import SETTINGS
from storage import Storage

log = logging.getLogger("webauthn")

class WebAuthnService:
    """
    Provides registration and authentication flows for admins with WebAuthn.
    """

    def __init__(self, store: Storage):
        rp = PublicKeyCredentialRpEntity(SETTINGS["RP_ID"], SETTINGS["RP_NAME"])
        self.server = Fido2Server(rp)
        self.store = store

    def _user_entity(self, admin_id: str) -> PublicKeyCredentialUserEntity:
        return PublicKeyCredentialUserEntity(admin_id.encode(), admin_id, admin_id)

    def registration_options(self, admin_id: str) -> Dict[str, Any]:
        """
        Generate PublicKeyCredentialCreationOptions for an admin.
        """
        options, state = self.server.register_begin(
            self._user_entity(admin_id),
            user_verification="required",
            authenticator_attachment="platform",
        )
        self.store.put("challenges", admin_id, state)
        log.info("Generated registration options for %s", admin_id)
        return options

    def verify_attestation(self, admin_id: str, attestation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify attestation and store credential.
        """
        state = self.store.get("challenges").get(admin_id)
        if not state:
            raise ValueError("Missing registration state.")
        auth_data = self.server.register_complete(state, attestation)
        credential_data = auth_data.credential_data
        cred = {
            "id": attestation["id"],
            "publicKeyPem": base64.b64encode(credential_data.public_key).decode(),
            "signCount": 0,
        }
        self.store.append_admin_credential(admin_id, cred)
        log.info("Stored credential for %s", admin_id)
        return cred

    def authentication_options(self, admin_id: str) -> Dict[str, Any]:
        """
        Generate PublicKeyCredentialRequestOptions for an admin.
        """
        creds = self.store.get("admins").get(admin_id, {}).get("credentials", [])
        if not creds:
            raise ValueError("No credentials for admin.")
        credential_ids = [c["id"].encode() for c in creds]
        options, state = self.server.authenticate_begin(
            credential_ids=credential_ids,
            user_verification="required",
        )
        self.store.put("challenges", admin_id, state)
        log.info("Generated authentication options for %s", admin_id)
        return options

    def verify_assertion(self, admin_id: str, assertion: Dict[str, Any]) -> bool:
        """
        Verify assertion using stored state; set session if valid.
        """
        state = self.store.get("challenges").get(admin_id)
        if not state:
            raise ValueError("Missing authentication state.")
        self.server.authenticate_complete(state, [assertion], assertion)
        log.info("Assertion valid for %s", admin_id)
        return True
