"""
OTP/TOTP service for participant authentication.
"""

import logging
import time
import io
import pyotp
import qrcode
from typing import Tuple
from storage import Storage

log = logging.getLogger("otp")

class OtpService:
    """
    Email OTP and TOTP provisioning/verification for participants.
    """

    def __init__(self, store: Storage, email_sender: dict):
        self.store = store
        self.email_sender = email_sender

    def generate_email_otp(self, email: str) -> str:
        """
        Generate a 6-digit OTP with 5-minute TTL and store it.
        """
        code = f"{int(time.time() * 1000) % 1000000:06d}"
        exp = int(time.time()) + 300
        self.store.put("otp", email, {"code": code, "exp": exp})
        log.info("Sending OTP to %s (code=%s, exp=%s)", email, code, exp)
        # TODO: integrate SMTP using self.email_sender
        return code

    def verify_email_otp(self, email: str, code: str) -> bool:
        """
        Verify email OTP against stored record and TTL.
        """
        rec = self.store.get("otp").get(email)
        if not rec:
            log.warning("No OTP for %s", email)
            return False
        if int(time.time()) > rec["exp"]:
            log.warning("Expired OTP for %s", email)
            return False
        ok = rec["code"] == code
        log.info("OTP verify for %s: %s", email, ok)
        return ok

    def provision_totp(self, email: str) -> Tuple[str, bytes]:
        """
        Provision a TOTP secret and return URI + QR PNG bytes.
        """
        users = self.store.get("users")
        user = users.get(email, {})
        secret = user.get("totp_secret") or pyotp.random_base32()
        user["totp_secret"] = secret
        self.store.put("users", email, user)
        uri = pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name="Camp Dashboard")

        qr_img = qrcode.make(uri)
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        log.info("Provisioned TOTP for %s", email)
        return uri, buf.getvalue()

    def verify_totp(self, email: str, code: str) -> bool:
        """
        Verify a TOTP code for a user.
        """
        user = self.store.get("users").get(email)
        if not user or not user.get("totp_secret"):
            log.warning("No TOTP secret for %s", email)
            return False
        ok = pyotp.TOTP(user["totp_secret"]).verify(code)
        log.info("TOTP verify for %s: %s", email, ok)
        return ok
