"""
Inspect the structure of chat messages from chat-downloader.
This script helps understand how emojis and other fields are structured.

Usage:
    python scripts/inspect_message_structure.py VIDEO_ID
"""

import json
import sys
from chat_downloader import ChatDownloader

def inspect_messages(video_id: str, max_messages: int = 5):
    """Inspect the first few messages from a video."""
    url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"Fetching messages from: {url}\n")

    downloader = ChatDownloader()
    chat = downloader.get_chat(url)

    for i, message in enumerate(chat):
        if i >= max_messages:
            break

        print(f"=" * 80)
        print(f"Message {i + 1}:")
        print("=" * 80)
        print(json.dumps(message, indent=2, ensure_ascii=False))
        print("\n")

        # Check for emoji-related fields
        if 'emotes' in message:
            print(f"Found 'emotes' field: {message['emotes']}")

        # Check message content
        msg_content = message.get('message', '')
        if ':' in msg_content and ('face-' in msg_content or 'emoji' in msg_content):
            print(f"Found potential emoji syntax in message: {msg_content}")

        print("\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/inspect_message_structure.py VIDEO_ID")
        print("Example: python scripts/inspect_message_structure.py dQw4w9WgXcQ")
        sys.exit(1)

    video_id = sys.argv[1]
    inspect_messages(video_id)
