import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=True)
else:
    load_dotenv()

DB_PATH = BASE_DIR / "doc_intelligence.db"
CACHE_DIR = BASE_DIR / "cache"
SAMPLE_DOCS_DIR = BASE_DIR / "sample_docs"

CACHE_DIR.mkdir(exist_ok=True)
SAMPLE_DOCS_DIR.mkdir(exist_ok=True)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# Business rules thresholds
HIGH_VALUE_THRESHOLD = 100000.0  # INR 1,00,000

def reload_config():
    global SARVAM_API_KEY, SLACK_WEBHOOK_URL
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE, override=True)
    SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
    return SARVAM_API_KEY
