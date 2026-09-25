from app.memory.database import get_connection


def get_memory_columns() -> set[str]:
    connection = get_connection()

    try:
        rows = connection.execute(
            "PRAGMA table_info(memories)"
        ).fetchall()

        return {
            row["name"]
            for row in rows
        }

    finally:
        connection.close()


def migrate_memory_v2() -> None:
    connection = get_connection()

    try:
        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(memories)"
            ).fetchall()
        }

        migrations = [
            (
                "source",
                """
                ALTER TABLE memories
                ADD COLUMN source TEXT NOT NULL DEFAULT 'manual'
                """,
            ),
            (
                "confidence",
                """
                ALTER TABLE memories
                ADD COLUMN confidence REAL NOT NULL DEFAULT 1.0
                """,
            ),
            (
                "tags",
                """
                ALTER TABLE memories
                ADD COLUMN tags TEXT NOT NULL DEFAULT ''
                """,
            ),
            (
                "access_count",
                """
                ALTER TABLE memories
                ADD COLUMN access_count INTEGER NOT NULL DEFAULT 0
                """,
            ),
            (
                "last_used_at",
                """
                ALTER TABLE memories
                ADD COLUMN last_used_at TEXT
                """,
            ),
            (
                "is_active",
                """
                ALTER TABLE memories
                ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1
                """,
            ),
            (
                "embedding",
                """
                ALTER TABLE memories
                ADD COLUMN embedding BLOB
                """,
            ),
        ]

        for column_name, sql in migrations:
            if column_name not in existing_columns:
                connection.execute(sql)

        connection.commit()

    finally:
        connection.close()