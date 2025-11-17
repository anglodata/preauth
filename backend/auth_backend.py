"""
FastAPI backend:
- Serves WebAuthn registration/login endpoints
- Serves static files (JS, CSS, images)
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any

from storage import Storage
from services.webauthn_service import WebAuthnService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("auth_backend")

app = FastAPI()


from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

app = FastAPI()
store = Storage("app_db.json")
webauthn = WebAuthnService(store=store)


# Sert les fichiers statiques (JS, CSS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response: Response = await call_next(request)
    # Politique CSP stricte : uniquement les ressources servies par ton backend
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; "      # par défaut, rien n'est autorisé
        "script-src 'self' /static/js https://cdn.jsdelivr.net;"  # seuls tes scripts JS locaux
        "style-src 'self' /static/css https://cdn.jsdelivr.net;"  # si tu ajoutes du CSS
        "img-src 'self' /static/img"      # si tu ajoutes des images
    )
    return response







class AdminId(BaseModel):
    adminId: str

@app.post("/webauthn/register/options")
def register_options(body: AdminId) -> Dict[str, Any]:
    return webauthn.registration_options(body.adminId)

@app.post("/webauthn/register/verify")
def register_verify(payload: Dict[str, Any]) -> Dict[str, Any]:
    admin_id = payload.get("adminId")
    att = payload.get("attestation")
    if not admin_id or not att:
        raise HTTPException(status_code=400, detail="Missing fields.")
    cred = webauthn.verify_attestation(admin_id, att)
    return {"ok": True, "credential": cred}

@app.post("/webauthn/login/options")
def login_options(body: AdminId) -> Dict[str, Any]:
    return webauthn.authentication_options(body.adminId)

@app.post("/webauthn/login/verify")
def login_verify(payload: Dict[str, Any]) -> Dict[str, Any]:
    admin_id = payload.get("adminId")
    assertion = payload.get("assertion")
    if not admin_id or not assertion:
        raise HTTPException(status_code=400, detail="Missing fields.")
    ok = webauthn.verify_assertion(admin_id, assertion)
    if ok:
        store.put("sessions", "admin", {"authenticated": True, "adminId": admin_id})
    return {"ok": ok}

@app.get("/session/admin")
def session_admin() -> Dict[str, Any]:
    return store.get("sessions").get("admin", {"authenticated": False})
