import os
from pathlib import Path
import sqlite3


# C:\atles
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# C:\atles\data
DATA_DIR = PROJECT_ROOT / "data"

# The app uses C:\atles\data\atles.db by default.
# Pytest sets ATLES_DATABASE_PATH to an isolated temporary database.
DATABASE_PATH = Path(
    os.environ.get("ATLES_DATABASE_PATH", DATA_DIR / "atles.db")
)


def ensure_database_directory() -> None:
    """Create the selected database directory if it does not exist."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Return a connection to the configured Atles SQLite database."""
    ensure_database_directory()

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection