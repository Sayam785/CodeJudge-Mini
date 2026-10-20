"""Application settings loaded from environment variables."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-this-local-secret-key")
ORACLE_USER = os.getenv("ORACLE_USER", "SAYAM_PBL")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "123")
ORACLE_DSN = os.getenv("ORACLE_DSN", "localhost:1521/XEPDB1")
MAX_SOURCE_BYTES = 64 * 1024
PORT = int(os.getenv("FLASK_PORT", "5000"))
