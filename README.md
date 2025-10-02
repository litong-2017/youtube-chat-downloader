# YouTube Chat Downloader

A powerful Python tool to download YouTube live stream chat history and store it in a SQLite database for analysis.

## Features

- 📥 Download chat history from YouTube live streams and replays
- 💾 Store data in SQLite database with optimized schema
- 🎨 Beautiful command-line interface with rich output
- 📊 Data analysis and export capabilities
- ⚡ Support for large channels with rate limiting
- 🔄 **Incremental downloads** (skip already processed videos)
- 📅 **Date range filtering** (download videos from specific time periods)
- 🎯 **Index range filtering** (download specific video ranges)
- 🌍 Multi-language support (English, Chinese, Korean, Japanese)

## Installation

```bash
# Clone the repository
git clone https://github.com/litong-2017/youtube-chat-downloader.git
cd youtube-chat-downloader

# Install using uv (recommended)
uv sync

# Or install in development mode with testing tools
uv sync --dev

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

## Alternative: Using the launcher scripts

For convenience, you can use the provided launcher scripts:

```bash
# Windows
ytchat.bat <command> [options]

# Linux/Mac
./ytchat.sh <command> [options]
```

Or run directly with Python:

```bash
# After activating virtual environment
python -m youtube_chat_downloader.cli.commands <command> [options]
```

## Quick Start

### 1. Download all chat history from a channel

```bash
# Download all livestreams from a channel (incremental mode by default)
ytchat download @channelname

# Download with custom database path
ytchat download @channelname --db-path my_data.db
```

### 2. Download with filters

```bash
# Download only the first 10 videos
ytchat download @channelname --max-videos 10

# Download videos from a specific date range
ytchat download @channelname --start-date 2024-01-01 --end-date 2024-12-31

# Download videos by index range (0-based)
ytchat download @channelname --start-index 0 --end-index 50

# Combine filters
ytchat download @channelname --start-date 2024-01-01 --max-videos 20
```

### 3. Incremental downloads

```bash
# Skip already downloaded videos (default behavior)
ytchat download @channelname --skip-existing

# Re-download everything (override existing data)
ytchat download @channelname --no-skip-existing
```

### 4. Validate a channel before downloading

```bash
# Check if channel exists and preview livestreams
ytchat validate @channelname
```

### 5. Analyze downloaded data

```bash
# Show statistics and top chatters
ytchat analyze

# With custom database path
ytchat analyze --db-path my_data.db
```

### 6. Export data to CSV

```bash
# Export all data
ytchat export --output all_chats.csv

# Export specific video
ytchat export --video-id VIDEO_ID --output video_chat.csv
```

### 7. List downloaded videos

```bash
# Show all videos in database
ytchat list-videos
```

## Command Reference

### `ytchat download`

Download chat history from a YouTube channel.

**Arguments:**
- `channel_id`: YouTube channel ID or handle (e.g., `@channelname`, `UC...`)

**Options:**
- `--max-videos, -m`: Maximum number of videos to process
- `--db-path, -d`: Database file path (default: `data/youtube_chat.db`)
- `--search-mode, -s`: Use search mode to find videos (fallback method)
- `--skip-existing / --no-skip-existing`: Skip already downloaded videos (default: True)
- `--start-date`: Start date for video range (YYYY-MM-DD)
- `--end-date`: End date for video range (YYYY-MM-DD)
- `--start-index`: Start index in video list (0-based)
- `--end-index`: End index in video list (exclusive)

**Examples:**
```bash
# Basic usage
ytchat download @pewdiepie

# Download latest 50 videos only
ytchat download @pewdiepie --max-videos 50

# Download videos from 2024
ytchat download @pewdiepie --start-date 2024-01-01 --end-date 2024-12-31

# Download videos 10-30 from the list
ytchat download @pewdiepie --start-index 10 --end-index 30

# Force re-download all videos
ytchat download @pewdiepie --no-skip-existing
```

### `ytchat validate`

Validate if a YouTube channel exists and preview available livestreams.

**Arguments:**
- `channel_id`: YouTube channel ID or handle

**Example:**
```bash
ytchat validate @channelname
```

### `ytchat analyze`

Analyze downloaded chat data and show statistics.

**Options:**
- `--db-path, -d`: Database file path (default: `data/youtube_chat.db`)

**Example:**
```bash
ytchat analyze
ytchat analyze --db-path custom.db
```

### `ytchat export`

Export chat data to CSV format.

**Options:**
- `--db-path, -d`: Database file path (default: `data/youtube_chat.db`)
- `--video-id, -v`: Export specific video (leave empty for all)
- `--output, -o`: Output CSV file path (default: `chat_export.csv`)

**Examples:**
```bash
# Export all data
ytchat export --output all_data.csv

# Export specific video
ytchat export --video-id dQw4w9WgXcQ --output video_chat.csv
```

### `ytchat list-videos`

List all downloaded videos in the database.

**Options:**
- `--db-path, -d`: Database file path (default: `data/youtube_chat.db`)

**Example:**
```bash
ytchat list-videos
```

## Database Schema

### Videos Table
- `video_id` (Primary Key): YouTube video ID
- `title`: Video title
- `upload_date`: Upload date (YYYYMMDD format, indexed)
- `duration`: Video duration in seconds
- `view_count`: Number of views
- `channel_id`: Channel ID (indexed)
- `channel_name`: Channel name
- `description`: Video description
- `is_live`: Currently live flag
- `was_live`: Was previously live flag
- `created_at`: Record creation timestamp

### Chat Messages Table
- `id` (Primary Key): Auto-increment ID
- `video_id`: Reference to video (indexed)
- `message_id`: Unique message identifier (indexed)
- `author_name`: Chat author username (indexed)
- `author_id`: Chat author ID (indexed)
- `message`: Chat message text
- `timestamp_usec`: Message timestamp in microseconds (indexed)
- `timestamp_text`: Human-readable timestamp
- `message_type`: Type of message (text, superchat, etc., indexed)
- `superchat_amount`: Super Chat amount (if applicable)
- `superchat_currency`: Super Chat currency
- `badges`: Author badges (JSON string)
- `created_at`: Record creation timestamp

## Advanced Usage

### Incremental Daily Updates

Set up a cron job or scheduled task to download new videos daily:

```bash
# Download new videos from multiple channels
ytchat download @channel1 --skip-existing
ytchat download @channel2 --skip-existing
ytchat download @channel3 --skip-existing
```

### Batch Processing

Process multiple channels with different date ranges:

```bash
#!/bin/bash
# download_all.sh

CHANNELS=("@channel1" "@channel2" "@channel3")

for channel in "${CHANNELS[@]}"; do
    echo "Processing $channel..."
    ytchat download "$channel" \
        --start-date 2024-01-01 \
        --skip-existing \
        --db-path "data/${channel//[@\/]/_}.db"
done
```

### Data Analysis with Python

```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('data/youtube_chat.db')

# Load chat messages
df = pd.read_sql_query("""
    SELECT cm.*, v.title, v.channel_name
    FROM chat_messages cm
    JOIN videos v ON cm.video_id = v.video_id
    WHERE v.upload_date >= '20240101'
""", conn)

# Analyze top chatters
top_users = df['author_name'].value_counts().head(10)
print(top_users)

# Find Super Chats
superchats = df[df['superchat_amount'].notna()]
total_revenue = superchats['superchat_amount'].sum()
print(f"Total Super Chat revenue: {total_revenue}")
```

## Troubleshooting

### Channel not found
- Make sure the channel ID is correct (try with `@` prefix or without)
- Try using `ytchat validate @channelname` to check
- Use `--search-mode` flag if direct channel access fails

### No chat messages found
- The video may not have had live chat enabled
- The video may be too old (chat replays expire after some time)
- Try a different video from the channel

### Rate limiting
- The tool automatically adds 2-second delays between videos
- For very large channels, consider downloading in batches using `--start-index` and `--end-index`

## Development

### Run tests
```bash
pytest
pytest --cov=src  # With coverage
```

### Code formatting
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video metadata extraction
- [chat-downloader](https://github.com/xenova/chat-downloader) - YouTube chat download functionality
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
