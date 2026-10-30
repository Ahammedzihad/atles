"""Keep pytest database writes in a temporary database."""

import os
import tempfile
from pathlib import Path


_TEST_DATABASE_DIRECTORY = tempfile.TemporaryDirectory(
    prefix="atles-pytest-"
)
_TEST_DATABASE_PATH = (
    Path(_TEST_DATABASE_DIRECTORY.name) / "atles-test.db"
)

os.environ["ATLES_DATABASE_PATH"] = str(_TEST_DATABASE_PATH)

from app.memory.models import create_tables

create_tables()
