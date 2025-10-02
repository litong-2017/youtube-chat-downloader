#!/usr/bin/env python3
"""Test script to validate channels and find livestreams."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from youtube_chat_downloader.core.downloader import YouTubeChatDownloader


def test_channel(channel_id: str):
    """Test channel access and video discovery."""
    print(f"🔍 Testing channel: {channel_id}")
    
    downloader = YouTubeChatDownloader()
    
    # Test 1: Get channel info
    print("\n1. Getting channel info...")
    try:
        channel_info = downloader._get_channel_info(channel_id.strip('@'))
        if channel_info:
            print(f"   ✅ Channel found: {channel_info.get('channel_name', 'Unknown')}")
            print(f"   📋 Channel ID: {channel_info.get('channel_id', 'Unknown')}")
            if channel_info.get('subscriber_count'):
                print(f"   👥 Subscribers: {channel_info['subscriber_count']:,}")
        else:
            print("   ❌ Channel not found or not accessible")
            print("   🔍 Will try to find videos through search...")
    except Exception as e:
        print(f"   ❌ Error getting channel info: {e}")
        channel_info = None
    
    # Test 2: Get livestream videos
    print("\n2. Getting livestream videos...")
    try:
        videos = downloader.get_channel_livestreams(channel_id)
        print(f"   📺 Found {len(videos)} videos")
        
        if videos:
            print("   Recent videos:")
            for i, video in enumerate(videos[:5], 1):
                title = video['title'][:60] + "..." if len(video['title']) > 60 else video['title']
                duration = f" ({video['duration']}s)" if video.get('duration') else ""
                was_live = " [LIVE]" if video.get('was_live') or video.get('is_live') else ""
                print(f"   {i}. {video['video_id']}: {title}{duration}{was_live}")
        else:
            print("   ❌ No videos found")
            return False
    except Exception as e:
        print(f"   ❌ Error getting videos: {e}")
        return False
    
    # Test 3: Try to get detailed info for first video
    if videos:
        print(f"\n3. Testing video info for: {videos[0]['video_id']}")
        try:
            video_info = downloader.get_video_info(videos[0]['video_id'])
            if video_info:
                print(f"   ✅ Video info retrieved")
                print(f"   📺 Title: {video_info['title'][:60]}...")
                print(f"   🕒 Duration: {video_info.get('duration', 'Unknown')} seconds")
                print(f"   👁️ Views: {video_info.get('view_count', 'Unknown'):,}")
                print(f"   📺 Was Live: {video_info.get('was_live', False)}")
                print(f"   🔴 Is Live: {video_info.get('is_live', False)}")
            else:
                print("   ❌ Could not get video info")
        except Exception as e:
            print(f"   ❌ Error getting video info: {e}")
    
    # Test 4: Try to check if chat is available for first video
    if videos:
        print(f"\n4. Testing chat availability for: {videos[0]['video_id']}")
        try:
            # Just try to get a few messages to test
            chat_messages = []
            from chat_downloader import ChatDownloader
            chat_downloader = ChatDownloader()
            
            url = f"https://www.youtube.com/watch?v={videos[0]['video_id']}"
            chat = chat_downloader.get_chat(url)
            
            # Get first few messages
            count = 0
            for message in chat:
                chat_messages.append(message)
                count += 1
                if count >= 5:  # Just get 5 messages for testing
                    break
            
            if chat_messages:
                print(f"   ✅ Chat available! Found {len(chat_messages)} sample messages")
                for i, msg in enumerate(chat_messages, 1):
                    author = msg.get('author', {}).get('name', 'Unknown') if msg.get('author') else 'Unknown'
                    text = str(msg.get('message', ''))[:40] + "..." if len(str(msg.get('message', ''))) > 40 else str(msg.get('message', ''))
                    print(f"   {i}. {author}: {text}")
            else:
                print("   ⚠️ No chat messages found (video might not have had chat enabled)")
                
        except Exception as e:
            print(f"   ❌ Chat not available or error: {e}")
    
    return len(videos) > 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_channel.py @channel_name")
        print("Examples:")
        print("  python test_channel.py @chenyifaer")
        print("  python test_channel.py @pewdiepie")
        print("  python test_channel.py UCxxxxxxxxxxxxxx")  # Channel ID format
        sys.exit(1)
    
    channel = sys.argv[1]
    success = test_channel(channel)
    
    print("\n" + "="*60)
    if success:
        print(f"🎉 Channel {channel} is ready for download!")
        print(f"To download: uv run ytchat download {channel} --max-videos 1")
    else:
        print(f"❌ Channel {channel} has issues. Please check:")
        print("1. Channel ID is correct")
        print("2. Channel exists and is public")
        print("3. Channel has livestream videos")
        print("4. Try a different channel for testing")
