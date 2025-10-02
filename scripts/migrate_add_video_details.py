"""
Migration script to add detailed video information fields to existing database.

This script adds the following fields to the videos table:
- live_start_timestamp
- live_end_timestamp
- release_timestamp
- thumbnail
- categories
- tags
- like_count
- comment_count
- live_status
- availability
- uploader
- uploader_id

Usage:
    python scripts/migrate_add_video_details.py [--db-path PATH]
"""

import argparse
import sqlite3
from pathlib import Path


def migrate_database(db_path: str):
    """Add new columns to the videos table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(videos)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Define new columns with their types
    new_columns = {
        'live_start_timestamp': 'BIGINT',
        'live_end_timestamp': 'BIGINT',
        'release_timestamp': 'BIGINT',
        'thumbnail': 'TEXT',
        'categories': 'TEXT',
        'tags': 'TEXT',
        'like_count': 'BIGINT',
        'comment_count': 'BIGINT',
        'live_status': 'VARCHAR(50)',
        'availability': 'VARCHAR(50)',
        'uploader': 'VARCHAR(100)',
        'uploader_id': 'VARCHAR(100)',
    }

    # Add missing columns
    added_count = 0
    for column_name, column_type in new_columns.items():
        if column_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE videos ADD COLUMN {column_name} {column_type}")
                print(f"✓ Added column: {column_name}")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"✗ Failed to add column {column_name}: {e}")

    conn.commit()
    conn.close()

    if added_count > 0:
        print(f"\n✓ Migration completed: {added_count} columns added")
    else:
        print("\n✓ Database already up to date")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate database to add detailed video information fields"
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
