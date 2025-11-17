"""
JSON-backed storage for demo purposes.
Replace with DB/cloud storage in production.
"""

import json
import logging
from typing import Any, Dict
from pathlib import Path

log = logging.getLogger("storage")

class Storage:
    """
    Simple JSON storage for users, admins, OTPs, challenges, sessions.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.exists():
            self._write({"users": {}, "admins": {}, "otp": {}, "challenges": {}, "sessions": {}})
        log.info("Storage initialized at %s", self.path)

    def _read(self) -> Dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: Dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        log.debug("Storage wrote to %s", self.path)

    def get(self, section: str) -> Dict[str, Any]:
        return self._read().get(section, {})

    def put(self, section: str, key: str, value: Any) -> None:
        data = self._read()
        data.setdefault(section, {})
        data[section][key] = value
        self._write(data)
        log.debug("Updated %s[%s]", section, key)

    def delete(self, section: str, key: str) -> None:
        data = self._read()
        if key in data.get(section, {}):
            del data[section][key]
        self._write(data)
        log.debug("Deleted %s[%s]", section, key)

    def append_admin_credential(self, admin_id: str, cred: Dict[str, Any]) -> None:
        data = self._read()
        admin = data.setdefault("admins", {}).setdefault(admin_id, {"credentials": []})
        admin["credentials"].append(cred)
        self._write(data)
        log.info("Appended credential for admin %s", admin_id)
