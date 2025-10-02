"""
Example script showing how to work with emojis in YouTube chat messages.

This demonstrates:
1. Querying messages with emojis
2. Extracting emoji information
3. Formatting messages with emojis
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.youtube_chat_downloader.core.analyzer import ChatAnalyzer
from src.youtube_chat_downloader.utils.emoji_handler import (
    extract_emote_info,
    format_message_with_emotes,
    emotes_to_markdown,
    get_emote_names,
    count_emotes,
    has_custom_emojis
)


def analyze_emojis_in_video(video_id: str, db_path: str = "data/youtube_chat.db"):
    """Analyze emoji usage in a video's chat."""
    analyzer = ChatAnalyzer(db_path)

    print(f"Analyzing emojis in video: {video_id}\n")

    # Get all messages for the video
    df = analyzer.get_chat_by_video(video_id)

    if df.empty:
        print("No messages found for this video")
        return

    # Filter messages with emotes
    messages_with_emotes = df[df['emotes'].notna()]

    print(f"Total messages: {len(df)}")
    print(f"Messages with custom emojis: {len(messages_with_emotes)}")
    print(f"Emoji usage rate: {len(messages_with_emotes) / len(df) * 100:.2f}%\n")

    if messages_with_emotes.empty:
        print("No custom emojis found in this video's chat")
        return

    # Show some examples
    print("=" * 80)
    print("Sample messages with emojis:")
    print("=" * 80)

    for idx, row in messages_with_emotes.head(10).iterrows():
        author = row['author_name']
        message = row['message']
        emotes_data = row['emotes']

        print(f"\nAuthor: {author}")
        print(f"Original: {message}")

        # Extract emote info
        emotes = extract_emote_info(emotes_data)
        if emotes:
            print(f"Emojis used: {get_emote_names(emotes_data)}")
            print(f"Formatted: {format_message_with_emotes(message, emotes_data)}")

            # Show detailed emote info
            for emote in emotes:
                print(f"  - {emote['name']}: {emote.get('url', 'No URL')}")

    # Emoji statistics
    print("\n" + "=" * 80)
    print("Emoji Statistics:")
    print("=" * 80)

    all_emoji_names = []
    for emotes_data in messages_with_emotes['emotes']:
        all_emoji_names.extend(get_emote_names(emotes_data))

    if all_emoji_names:
        from collections import Counter
        emoji_counts = Counter(all_emoji_names)

        print("\nTop 10 most used emojis:")
        for emoji, count in emoji_counts.most_common(10):
            print(f"  {emoji}: {count} times")


def export_messages_with_emojis(
    video_id: str,
    output_file: str = "messages_with_emojis.txt",
    db_path: str = "data/youtube_chat.db"
):
    """Export messages containing emojis to a text file."""
    analyzer = ChatAnalyzer(db_path)

    df = analyzer.get_chat_by_video(video_id)
    messages_with_emotes = df[df['emotes'].notna()]

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Messages with Emojis - Video: {video_id}\n")
        f.write("=" * 80 + "\n\n")

        for idx, row in messages_with_emotes.iterrows():
            f.write(f"[{row['timestamp_text']}] {row['author_name']}\n")
            f.write(f"Message: {row['message']}\n")

            formatted = format_message_with_emotes(row['message'], row['emotes'])
            if formatted != row['message']:
                f.write(f"Formatted: {formatted}\n")

            emotes = extract_emote_info(row['emotes'])
            if emotes:
                f.write("Emojis:\n")
                for emote in emotes:
                    f.write(f"  - {emote['name']}: {emote.get('url', 'N/A')}\n")

            f.write("\n" + "-" * 80 + "\n\n")

    print(f"Exported to: {output_file}")


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python examples/emoji_usage.py VIDEO_ID [DB_PATH]")
        print("Example: python examples/emoji_usage.py dQw4w9WgXcQ")
        sys.exit(1)

    video_id = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else "data/youtube_chat.db"

    analyze_emojis_in_video(video_id, db_path)

    # Optionally export to file
    # export_messages_with_emojis(video_id, f"{video_id}_emojis.txt", db_path)
