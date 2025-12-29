#!/bin/bash
echo "Starting Bookly Application..."
echo "=============================="
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Launching FastAPI server..."
echo "=============================="
fastapi dev main.py
