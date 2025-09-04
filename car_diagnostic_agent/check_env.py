#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment variables:")
print(f"  enable_mock_mode: {os.getenv('enable_mock_mode')}")
print(f"  GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY')[:10] if os.getenv('GOOGLE_API_KEY') else None}...")

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.obd_config import config_manager
print(f"Mock mode enabled (from config manager): {config_manager.is_mock_mode_enabled()}")