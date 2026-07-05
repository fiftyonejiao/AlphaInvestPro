import os
import sys
from pathlib import Path

# Ensure a clean, key-free environment and isolated test database BEFORE
# app modules load their settings.
os.environ.pop("QVERIS_API_KEY", None)
os.environ.pop("DEEPSEEK_API_KEY", None)
os.environ["DATABASE_URL"] = "sqlite:///./test_alphainvestpro.db"
os.environ["ANALYSIS_STEP_DELAY_SECONDS"] = "0"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402

from app.storage.database import init_db, engine, Base  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def _database():
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)
    db_file = Path("./test_alphainvestpro.db")
    if db_file.exists():
        db_file.unlink()
