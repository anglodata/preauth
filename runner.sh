#!/bin/bash
echo "🚀 Starting Camp Dashboard..."
uvicorn backend.auth_backend:app --port 8000 &
streamlit run app.py
