import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

TEST_ENV_DEFAULTS = {
    "DB_NAME": "etir_test",
    "DB_USER": "etir_test",
    "DB_PASSWORD": "etir_test",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
}
for key, value in TEST_ENV_DEFAULTS.items():
    os.environ.setdefault(key, value)
