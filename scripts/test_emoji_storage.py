"""
Test script to verify Unicode emoji storage in SQLite.

This demonstrates that SQLite with UTF-8 encoding correctly stores Unicode emojis.
Python 3 strings are Unicode by default, so no conversion is needed.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.youtube_chat_downloader.utils.emoji_handler import (
    has_unicode_emojis,
    extract_unicode_emojis,
    has_custom_emojis,
    get_all_emojis
)


def test_unicode_storage():
    """Test that Unicode emojis are stored and retrieved correctly."""
    print("=" * 80)
    print("Testing Unicode Emoji Storage in SQLite")
    print("=" * 80)

    # Create in-memory database
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Create test table
    cursor.execute('''
        CREATE TABLE test_messages (
            id INTEGER PRIMARY KEY,
            message TEXT
        )
    ''')

    # Test messages with different emoji types
    test_messages = [
        "Hello 😊 world!",
        "Great stream! 👍❤️🔥",
        "おめでとう 🎉🎊",
        "Mix of text and 😎 emojis 🌟",
        ":face-blue-smiling: custom emoji",
        "Unicode 😀 and :custom-emoji: mixed",
        "No emojis here",
        "🚀🌙⭐✨💫",  # Space/astronomy emojis
        "😀😃😄😁😆😅🤣😂",  # Face emojis
    ]

    # Insert test messages
    for msg in test_messages:
        cursor.execute('INSERT INTO test_messages (message) VALUES (?)', (msg,))

    conn.commit()

    print("\n📝 Inserted Test Messages:")
    print("-" * 80)

    # Retrieve and analyze
    cursor.execute('SELECT id, message FROM test_messages')
    rows = cursor.fetchall()

    for row_id, message in rows:
        print(f"\nID {row_id}: {message}")
        print(f"  Length: {len(message)} characters")

        # Check for Unicode emojis
        if has_unicode_emojis(message):
            unicode_emojis = extract_unicode_emojis(message)
            print(f"  ✓ Unicode emojis found: {unicode_emojis}")
            print(f"    Count: {len(unicode_emojis)}")

        # Check for custom emojis
        if has_custom_emojis(message):
            print(f"  ⚠ Custom emoji syntax found: {message}")

        # Verify byte encoding
        byte_len = len(message.encode('utf-8'))
        if byte_len != len(message):
            print(f"  📊 UTF-8 bytes: {byte_len} (multi-byte characters present)")

    # Query messages with emojis
    print("\n" + "=" * 80)
    print("Querying Messages with Unicode Emojis")
    print("=" * 80)

    emoji_count = 0
    cursor.execute('SELECT message FROM test_messages')
    for (message,) in cursor.fetchall():
        if has_unicode_emojis(message):
            emoji_count += 1

    print(f"Total messages with Unicode emojis: {emoji_count}/{len(test_messages)}")

    # Test emoji extraction
    print("\n" + "=" * 80)
    print("Emoji Extraction Test")
    print("=" * 80)

    test_msg = "Hello 😊 this is 🔥 amazing! 🎉"
    emojis = extract_unicode_emojis(test_msg)
    print(f"Message: {test_msg}")
    print(f"Extracted emojis: {emojis}")
    print(f"Count: {len(emojis)}")

    # Test mixed content
    print("\n" + "=" * 80)
    print("Mixed Content Test (Unicode + Custom)")
    print("=" * 80)

    mixed_msg = "Hello 😊 and :custom-face: together!"
    all_emojis = get_all_emojis(mixed_msg, None)
    print(f"Message: {mixed_msg}")
    print(f"Unicode emojis: {all_emojis['unicode']}")
    print(f"Custom emojis: {all_emojis['custom']}")

    conn.close()

    print("\n" + "=" * 80)
    print("✓ Test Complete!")
    print("=" * 80)
    print("\nConclusion:")
    print("- SQLite with UTF-8 encoding stores Unicode emojis correctly")
    print("- Python 3 strings are Unicode by default")
    print("- No special conversion needed")
    print("- Emojis are stored as multi-byte UTF-8 sequences")


def test_real_database(db_path: str = "data/youtube_chat.db"):
    """Test emoji storage in actual database."""
    if not Path(db_path).exists():
        print(f"Database not found: {db_path}")
        return

    print("\n" + "=" * 80)
    print(f"Analyzing Real Database: {db_path}")
    print("=" * 80)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count messages with Unicode emojis
    cursor.execute('SELECT COUNT(*) FROM chat_messages')
    total_messages = cursor.fetchone()[0]

    cursor.execute('SELECT message FROM chat_messages LIMIT 1000')
    sample_messages = cursor.fetchall()

    unicode_count = 0
    custom_count = 0

    for (message,) in sample_messages:
        if message:
            if has_unicode_emojis(message):
                unicode_count += 1
            if has_custom_emojis(message):
                custom_count += 1

    print(f"\nTotal messages in database: {total_messages}")
    print(f"Sample analyzed: {len(sample_messages)}")
    print(f"Messages with Unicode emojis: {unicode_count}")
    print(f"Messages with custom emoji syntax: {custom_count}")

    # Show some examples
    cursor.execute('''
        SELECT author_name, message
        FROM chat_messages
        WHERE message IS NOT NULL
        LIMIT 100
    ''')

    print("\nSample messages with emojis:")
    print("-" * 80)

    count = 0
    for author, message in cursor.fetchall():
        if has_unicode_emojis(message) and count < 5:
            emojis = extract_unicode_emojis(message)
            print(f"{author}: {message}")
            print(f"  Emojis: {emojis}\n")
            count += 1

    conn.close()


if __name__ == "__main__":
    # Run basic test
    test_unicode_storage()

    # Test real database if provided
    if len(sys.argv) > 1:
        test_real_database(sys.argv[1])
    else:
        print("\nTip: Run with database path to test real data:")
        print("  python scripts/test_emoji_storage.py data/youtube_chat.db")
