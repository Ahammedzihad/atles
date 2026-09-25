from pathlib import Path
import sqlite3


# C:\atles
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# C:\atles\data
DATA_DIR = PROJECT_ROOT / "data"

# C:\atles\data\atles.db
DATABASE_PATH = DATA_DIR / "atles.db"


def ensure_database_directory() -> None:
    """Create the Atles data directory if it does not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Return a connection to the Atles SQLite database."""
    ensure_database_directory()

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection