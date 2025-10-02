#!/usr/bin/env python3
"""
YouTube Chat Downloader - Python API Usage Examples

This file demonstrates how to use the downloader programmatically
instead of using the CLI.
"""

import sys
from pathlib import Path

# Add parent directory to path to import the package
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from youtube_chat_downloader.core.downloader import YouTubeChatDownloader
from youtube_chat_downloader.core.analyzer import ChatAnalyzer


def example_1_basic_download():
    """Example 1: Basic channel download"""
    print("Example 1: Basic Download")
    print("-" * 50)

    # Create downloader instance
    downloader = YouTubeChatDownloader(db_path="data/example.db")

    # Download chat history for a channel
    # Replace with actual channel ID
    channel_id = "@examplechannel"

    print(f"Downloading chat history for {channel_id}...")
    downloader.download_channel_chat_history(
        channel_id=channel_id,
        max_videos=5,  # Limit to 5 videos for testing
        skip_existing=True
    )
    print("Download complete!\n")


def example_2_date_range_download():
    """Example 2: Download with date range filter"""
    print("Example 2: Date Range Download")
    print("-" * 50)

    downloader = YouTubeChatDownloader(db_path="data/example.db")

    # Download videos from 2024 only
    downloader.download_channel_chat_history(
        channel_id="@examplechannel",
        start_date="2024-01-01",
        end_date="2024-12-31",
        skip_existing=True
    )
    print("Date range download complete!\n")


def example_3_index_range_download():
    """Example 3: Download with index range"""
    print("Example 3: Index Range Download")
    print("-" * 50)

    downloader = YouTubeChatDownloader(db_path="data/example.db")

    # Download videos 0-10 from the list
    downloader.download_channel_chat_history(
        channel_id="@examplechannel",
        start_index=0,
        end_index=10,
        skip_existing=True
    )
    print("Index range download complete!\n")


def example_4_validate_channel():
    """Example 4: Validate channel before downloading"""
    print("Example 4: Channel Validation")
    print("-" * 50)

    downloader = YouTubeChatDownloader()

    channel_id = "@examplechannel"
    print(f"Validating channel: {channel_id}")

    # Get channel info
    channel_info = downloader._get_channel_info(channel_id.strip('@'))

    if channel_info:
        print(f"✅ Channel found!")
        print(f"  Name: {channel_info.get('channel_name')}")
        print(f"  ID: {channel_info.get('channel_id')}")
        print(f"  URL: {channel_info.get('channel_url')}")

        # Get livestreams
        videos = downloader.get_channel_livestreams(channel_id)
        print(f"  Livestreams found: {len(videos)}")

        if videos:
            print("\n  First 3 videos:")
            for i, video in enumerate(videos[:3], 1):
                print(f"    {i}. {video['title'][:50]}... ({video['video_id']})")
    else:
        print("❌ Channel not found!")

    print()


def example_5_analyze_data():
    """Example 5: Analyze downloaded data"""
    print("Example 5: Data Analysis")
    print("-" * 50)

    analyzer = ChatAnalyzer(db_path="data/example.db")

    # Get statistics
    stats = analyzer.get_statistics()
    print(f"Total videos: {stats['video_count']}")
    print(f"Total messages: {stats['message_count']}")

    # Get top chatters
    top_chatters = analyzer.get_top_chatters(limit=5)
    if not top_chatters.empty:
        print("\nTop 5 Chatters:")
        for idx, row in top_chatters.iterrows():
            print(f"  {row['author_name']}: {row['message_count']} messages")

    # Get top videos
    if stats['top_videos']:
        print("\nTop Videos by Message Count:")
        for video_id, count in stats['top_videos']:
            print(f"  {video_id}: {count} messages")

    print()


def example_6_export_data():
    """Example 6: Export data to CSV"""
    print("Example 6: Export to CSV")
    print("-" * 50)

    analyzer = ChatAnalyzer(db_path="data/example.db")

    # Export all data
    output_file = "data/export_example.csv"
    print(f"Exporting data to {output_file}...")
    analyzer.export_to_csv(output_file=output_file)
    print("Export complete!\n")


def example_7_get_video_info():
    """Example 7: Get specific video information"""
    print("Example 7: Get Video Info")
    print("-" * 50)

    downloader = YouTubeChatDownloader()

    # Replace with actual video ID
    video_id = "dQw4w9WgXcQ"
    print(f"Getting info for video: {video_id}")

    video_info = downloader.get_video_info(video_id)
    if video_info:
        print(f"  Title: {video_info['title']}")
        print(f"  Channel: {video_info['channel_name']}")
        print(f"  Duration: {video_info['duration']} seconds")
        print(f"  Views: {video_info['view_count']}")
        print(f"  Was Live: {video_info['was_live']}")
    else:
        print("  Video not found or error occurred")

    print()


def example_8_download_single_video():
    """Example 8: Download chat for a single video"""
    print("Example 8: Download Single Video Chat")
    print("-" * 50)

    downloader = YouTubeChatDownloader(db_path="data/example.db")

    # Replace with actual video ID
    video_id = "dQw4w9WgXcQ"
    print(f"Downloading chat for video: {video_id}")

    # Download chat messages
    messages = downloader.download_chat_for_video(video_id)
    print(f"Downloaded {len(messages)} messages")

    # Save to database
    if messages:
        downloader.save_chat_messages_to_db(messages)
        print("Messages saved to database!")

    print()


def main():
    """Run all examples"""
    print("=" * 50)
    print("YouTube Chat Downloader - Python API Examples")
    print("=" * 50)
    print()

    # Uncomment the examples you want to run:

    # example_1_basic_download()
    # example_2_date_range_download()
    # example_3_index_range_download()
    example_4_validate_channel()
    # example_5_analyze_data()
    # example_6_export_data()
    # example_7_get_video_info()
    # example_8_download_single_video()

    print("=" * 50)
    print("Examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
