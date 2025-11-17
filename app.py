"""
Streamlit frontend:
- User login via OTP/TOTP
- Admin login via WebAuthn (biometrics)
References external JS served by FastAPI at /static/js/
"""

import streamlit as st
import requests
from config import SETTINGS
from services.otp_service import OtpService
from storage import Storage

store = Storage(SETTINGS["DB_PATH"])
otp = OtpService(store=store, email_sender=SETTINGS["EMAIL_SENDER"])

ADMIN_SESSION_KEY = "admin_authenticated"
USER_SESSION_KEY = "user_authenticated"

st.set_page_config(page_title="Camp Dashboard", layout="centered")
st.title("Camp Dashboard")

tab_user, tab_admin = st.tabs(["Participants", "Admin"])

with tab_user:
    st.subheader("Connexion participants (OTP/TOTP)")
    email = st.text_input("Email")
    method = st.radio("Méthode", ["OTP email", "TOTP (Google Authenticator)"])
    if st.button("Envoyer OTP"):
        otp.generate_email_otp(email)
        st.info("Code OTP envoyé par email.")
    code = st.text_input("Code")
    if st.button("Valider"):
        ok = otp.verify_email_otp(email, code) if method == "OTP email" else otp.verify_totp(email, code)
        if ok:
            st.success("Connexion réussie ✅")
            st.session_state[USER_SESSION_KEY] = True
        else:
            st.error("Code invalide ❌")

with tab_admin:
    st.subheader("Connexion admin via biométrie (WebAuthn)")
    admin_id = st.text_input("Identifiant admin", value="admin@example.com")

    html = f"""
<div>
  <p id="status"></p>
  <button id="btn-register">Enregistrer une passkey</button>
  <button id="btn-login">Se connecter via passkey</button>

  <script>
    window.__CONFIG__ = {{
      ADMIN_ID: "{admin_id}",
      BACKEND_URL: "{SETTINGS['AUTH_BACKEND_BASE_URL']}"
    }};
  </script>
  <script src="{SETTINGS['AUTH_BACKEND_BASE_URL']}/static/js/webauthn.js"></script>
  <script src="{SETTINGS['AUTH_BACKEND_BASE_URL']}/static/js/admin_actions.js"></script>
</div>
"""
    st.components.v1.html(html, height=200)

    if st.button("Rafraîchir état admin"):
        r = requests.get(f"{SETTINGS['AUTH_BACKEND_BASE_URL']}/session/admin")
        if r.ok and r.json().get("authenticated"):
            st.success("Admin connecté ✅")
            st.session_state[ADMIN_SESSION_KEY] = True
        else:
            st.info("Admin non connecté.")
