# Camp Dashboard — Clean architecture (WebAuthn biometrics + OTP/TOTP)

This project implements:
- Admin authentication via device biometrics (WebAuthn passkeys).
- Participant authentication via email OTP or TOTP (Google Authenticator).
- Streamlit frontend, FastAPI backend, no inline JS — all scripts external.

## Run

1. Create venv and install:
python -m venv .venv source .venv/bin/activate pip install -r requirements.txt
2. Start backend:
uvicorn backend.auth_backend:app --reload --port 8000
3. Start Streamlit:
streamlit run app.py

Open the app in your browser:
- Admin tab: register and login via passkey (Face ID, fingerprint, etc.).
- Participants tab: OTP/TOTP flows.

## Notes

- Set `config.py` RP_ID to your HTTPS domain in production.
- Replace `storage.py` with a durable DB for real deployments.
- Integrate SMTP in `OtpService` for email sending.

## Security highlights

- Admin flow forces platform authenticator + user verification (biometrics/PIN).
- No fallback for admin — explicit design choice.
- OTP codes expire in 5 minutes; TOTP via RFC 6238.

https://copilot.microsoft.com/chats/czE5mgVjLmvAnAF2NTXSj