"""
Application configuration.
"""

SETTINGS = {
    "AUTH_BACKEND_BASE_URL": "http://localhost:8000",
    "DB_PATH": "app_db.json",
    "EMAIL_SENDER": {"from": "noreply@camp.example", "smtp": "smtp.example", "user": "", "password": ""},
    "RP_ID": "localhost",  # Use your HTTPS domain in production
    "RP_NAME": "Camp Dashboard",
}
