"""
Migration script to add emotes field to chat_messages table.

This script adds the 'emotes' field to store YouTube custom emoji information.

Usage:
    python scripts/migrate_add_emotes.py [--db-path PATH]
"""

import argparse
import sqlite3
from pathlib import Path


def migrate_database(db_path: str):
    """Add emotes column to the chat_messages table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(chat_messages)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Add emotes column if it doesn't exist
    if 'emotes' not in existing_columns:
        try:
            cursor.execute("ALTER TABLE chat_messages ADD COLUMN emotes TEXT")
            print("✓ Added column: emotes")
            conn.commit()
            print("\n✓ Migration completed successfully")
        except sqlite3.OperationalError as e:
            print(f"✗ Failed to add column emotes: {e}")
    else:
        print("✓ Database already up to date")

    conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Migrate database to add emotes field to chat_messages table"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="data/youtube_chat.db",
        help="Path to the database file (default: data/youtube_chat.db)",
    )

    args = parser.parse_args()

    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"✗ Database not found: {db_path}")
        print("  No migration needed - new database will be created with all fields")
        return

    print(f"Migrating database: {db_path}")
    migrate_database(str(db_path))


if __name__ == "__main__":
    main()
