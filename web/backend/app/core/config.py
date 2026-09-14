"""Application configuration: filesystem paths for DB and content."""

from pathlib import Path

BACKEND_DIR: Path = Path(__file__).resolve().parents[2]
DATA_DIR: Path = BACKEND_DIR / "data"
DB_PATH: Path = DATA_DIR / "runs.db"
CONTENT_DIR: Path = Path(__file__).resolve().parents[1] / "content"
FRONTEND_DIST: Path = BACKEND_DIR.parent / "frontend" / "dist"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
