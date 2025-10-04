# YouTube Chat Downloader

A powerful Python tool to download YouTube live stream chat history with flexible storage options (JSON files and/or databases).

## Features

- 📥 Download chat history from YouTube live streams and replays
- 💾 **JSON-first architecture** (default: save to JSON files, optional database storage)
- 🗄️ **Flexible database support** (SQLite or DuckDB)
- 🔐 **Cookies authentication** (bypass bot detection with browser cookies)
- 🎨 Beautiful command-line interface with rich output
- 📊 Data analysis and export capabilities
- ⚡ Support for large channels with rate limiting
- 🔄 **Incremental downloads** (skip or stop on already processed videos)
- 📅 **Date range filtering** (download videos from specific time periods)
- 🎯 **Index range filtering** (download specific video ranges)
- 📝 **Extended video metadata** (livestream timestamps, thumbnails, engagement metrics)
- 🔁 **JSON import** (import previously downloaded JSON files to database)
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

### 1. Download chat history (JSON-first approach - recommended)

```bash
# Download to JSON files only (default behavior)
ytchat download @channelname

# Download with cookies (bypass bot detection)
ytchat download @channelname --cookies www.youtube.com_cookies.txt

# Download to JSON with custom directory
ytchat download @channelname --json-dir custom_exports/

# Download to both JSON and SQLite database
ytchat download @channelname --save-to-db

# Download to both JSON and DuckDB database
ytchat download @channelname --save-to-db --db-type duckdb
```

### 2. Import JSON to database

```bash
# Import a JSON file to SQLite database
ytchat import-json data/json_exports/20251004_abc123.json

# Import to DuckDB
ytchat import-json data/json_exports/20251004_abc123.json --db-type duckdb

# Import with custom database path
ytchat import-json data/json_exports/20251004_abc123.json --db-path custom.db
```

### 3. Download with filters

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

### 4. Incremental downloads

```bash
# Skip already downloaded videos (default behavior)
ytchat download @channelname --skip-existing

# Stop when first already-downloaded video is encountered (default, efficient for updates)
ytchat download @channelname --stop-on-existing

# Continue processing all videos even if some are already downloaded
ytchat download @channelname --no-stop-on-existing

# Re-download everything (override existing data)
ytchat download @channelname --no-skip-existing
```

### 5. Validate a channel before downloading

```bash
# Check if channel exists and preview livestreams
ytchat validate @channelname
```

### 6. Analyze downloaded data

```bash
# Show statistics and top chatters (requires database)
ytchat analyze

# Analyze DuckDB database
ytchat analyze --db-type duckdb

# With custom database path
ytchat analyze --db-path my_data.db
```

### 7. Export data to CSV

```bash
# Export all data (requires database)
ytchat export --output all_chats.csv

# Export specific video
ytchat export --video-id VIDEO_ID --output video_chat.csv

# Export from DuckDB
ytchat export --db-type duckdb --output all_chats.csv
```

### 8. List downloaded videos

```bash
# Show all videos in database
ytchat list-videos

# List from DuckDB
ytchat list-videos --db-type duckdb
```

## Command Reference

### `ytchat download`

Download chat history from a YouTube channel.

**Arguments:**
- `channel_id`: YouTube channel ID or handle (e.g., `@channelname`, `UC...`)

**Options:**
- `--max-videos, -m`: Maximum number of videos to process
- `--db-path, -d`: Database file path (default: `data/youtube_chat.db`)
- `--db-type`: Database type: `sqlite` or `duckdb` (default: `sqlite`)
- `--json-dir`: Directory for JSON exports (default: `data/json_exports/`)
- `--save-to-db / --no-save-to-db`: Save to database in addition to JSON (default: False)
- `--cookies, -c`: Path to cookies file in Netscape format (bypass bot detection)
- `--search-mode, -s`: Use search mode to find videos (fallback method)
- `--skip-existing / --no-skip-existing`: Skip already downloaded videos (default: True)
- `--stop-on-existing / --no-stop-on-existing`: Stop when first downloaded video is found (default: True)
- `--start-date`: Start date for video range (YYYY-MM-DD)
- `--end-date`: End date for video range (YYYY-MM-DD)
- `--start-index`: Start index in video list (0-based)
- `--end-index`: End index in video list (exclusive)

**Examples:**
```bash
# Basic usage (JSON only)
ytchat download @pewdiepie

# Download with cookies to bypass bot detection
ytchat download @pewdiepie --cookies www.youtube.com_cookies.txt

# Download to both JSON and SQLite
ytchat download @pewdiepie --save-to-db

# Download to both JSON and DuckDB
ytchat download @pewdiepie --save-to-db --db-type duckdb

# Download latest 50 videos only
ytchat download @pewdiepie --max-videos 50

# Download videos from 2024
ytchat download @pewdiepie --start-date 2024-01-01 --end-date 2024-12-31

# Download videos 10-30 from the list
ytchat download @pewdiepie --start-index 10 --end-index 30

# Force re-download all videos
ytchat download @pewdiepie --no-skip-existing

# Continue downloading even if some videos are already downloaded
ytchat download @pewdiepie --no-stop-on-existing
```

### `ytchat import-json`

Import a previously downloaded JSON file to database.

**Arguments:**
- `json_file`: Path to the JSON file to import

**Options:**
- `--db-path, -d`: Database file path (default: `data/youtube_chat.db`)
- `--db-type`: Database type: `sqlite` or `duckdb` (default: `sqlite`)

**Examples:**
```bash
# Import to SQLite
ytchat import-json data/json_exports/20251004_abc123.json

# Import to DuckDB
ytchat import-json data/json_exports/20251004_abc123.json --db-type duckdb

# Import with custom database path
ytchat import-json data/json_exports/20251004_abc123.json --db-path custom.db
```

### `ytchat validate`

Validate if a YouTube channel exists and preview available livestreams.

**Arguments:**
- `channel_id`: YouTube channel ID or handle

**Options:**
- `--db-type`: Database type: `sqlite` or `duckdb` (default: `sqlite`)
- `--cookies, -c`: Path to cookies file in Netscape format

**Example:**
```bash
ytchat validate @channelname
ytchat validate @channelname --cookies www.youtube.com_cookies.txt
ytchat validate @channelname --db-type duckdb
```

### `ytchat analyze`

Analyze downloaded chat data and show statistics (requires database).

**Options:**
- `--db-path, -d`: Database file path (default: `data/youtube_chat.db`)
- `--db-type`: Database type: `sqlite` or `duckdb` (default: `sqlite`)

**Example:**
```bash
ytchat analyze
ytchat analyze --db-type duckdb
ytchat analyze --db-path custom.db
```

### `ytchat export`

Export chat data to CSV format (requires database).

**Options:**
- `--db-path, -d`: Database file path (default: `data/youtube_chat.db`)
- `--db-type`: Database type: `sqlite` or `duckdb` (default: `sqlite`)
- `--video-id, -v`: Export specific video (leave empty for all)
- `--output, -o`: Output CSV file path (default: `chat_export.csv`)

**Examples:**
```bash
# Export all data from SQLite
ytchat export --output all_data.csv

# Export from DuckDB
ytchat export --db-type duckdb --output all_data.csv

# Export specific video
ytchat export --video-id dQw4w9WgXcQ --output video_chat.csv
```

### `ytchat list-videos`

List all downloaded videos in the database (requires database).

**Options:**
- `--db-path, -d`: Database file path (default: `data/youtube_chat.db`)
- `--db-type`: Database type: `sqlite` or `duckdb` (default: `sqlite`)

**Example:**
```bash
ytchat list-videos
ytchat list-videos --db-type duckdb
```

## Data Storage

### JSON Files (Default)

By default, data is saved to JSON files in `data/json_exports/` directory:

**Filename format:** `YYYYMMDD_videoID.json` (based on upload date)

**JSON structure:**
```json
{
  "video_info": {
    "video_id": "abc123",
    "title": "Video title",
    "upload_date": "20251004",
    "duration": 3600,
    "view_count": 10000,
    "channel_id": "UC...",
    "channel_name": "Channel Name",
    "description": "...",
    "is_live": false,
    "was_live": true,
    "live_start_timestamp": 1728000000,
    "live_end_timestamp": 1728003600,
    "thumbnail": "https://...",
    "categories": ["Gaming"],
    "tags": ["tag1", "tag2"],
    "like_count": 500,
    "comment_count": 100
  },
  "chat_messages": [
    {
      "message_id": "msg_123",
      "author_name": "User",
      "author_id": "author_id",
      "message": "Hello!",
      "timestamp_usec": 1728000001000000,
      "message_type": "text_message",
      "badges": "[\"moderator\"]"
    }
  ],
  "export_metadata": {
    "export_time": "2025-10-04T12:00:00",
    "total_messages": 1234
  }
}
```

### Database Schema (Optional)

When using `--save-to-db`, data is stored in SQLite or DuckDB:

**Videos Table:**
- `video_id` (Primary Key): YouTube video ID
- `title`: Video title
- `upload_date`: Upload date (YYYYMMDD format, indexed)
- `duration`: Video duration in seconds
- `view_count`: Number of views (indexed)
- `channel_id`: Channel ID (indexed)
- `channel_name`: Channel name
- `description`: Video description
- `is_live`: Currently live flag
- `was_live`: Was previously live flag (indexed)
- `live_start_timestamp`: Livestream start time (indexed)
- `live_end_timestamp`: Livestream end time
- `release_timestamp`: Video release time
- `thumbnail`: Thumbnail URL
- `categories`: Categories (JSON array)
- `tags`: Tags (JSON array)
- `like_count`: Number of likes
- `comment_count`: Number of comments
- `live_status`: Livestream status (indexed)
- `availability`: Video availability
- `uploader`: Uploader name
- `uploader_id`: Uploader ID
- `created_at`: Record creation timestamp

**Chat Messages Table:**
- `id` (Primary Key): Auto-increment ID
- `video_id`: Reference to video (indexed)
- `message_id`: Unique message identifier (unique, indexed)
- `author_name`: Chat author username (indexed)
- `author_id`: Chat author ID (indexed)
- `message`: Chat message text
- `timestamp_usec`: Message timestamp in microseconds (indexed)
- `message_type`: Type of message (text, superchat, etc., indexed)
- `superchat_amount`: Super Chat amount (if applicable)
- `superchat_currency`: Super Chat currency
- `badges`: Author badges (JSON string)
- `created_at`: Record creation timestamp

**Composite Indexes:**
- `(video_id, timestamp_usec)`: Optimized for chronological message queries
- `(author_id, video_id)`: Optimized for user activity queries
- `(message_type, video_id)`: Optimized for message type filtering

## Recommended Workflows

### Workflow 1: JSON-First (Recommended)

Download to JSON files first, then selectively import to database:

```bash
# Step 1: Download to JSON only (fast, provides backup)
ytchat download @channel --max-videos 100

# Step 2: Inspect/process JSON files as needed
# Files are in data/json_exports/YYYYMMDD_videoID.json

# Step 3: Import selected JSON files to database for analysis
ytchat import-json data/json_exports/20251004_abc123.json

# Step 4: Analyze in database
ytchat analyze
ytchat export --output analysis.csv
```

### Workflow 2: Direct to Database

Download directly to database for immediate analysis:

```bash
# Download to both JSON and SQLite
ytchat download @channel --save-to-db

# Or download to DuckDB for better analytical performance
ytchat download @channel --save-to-db --db-type duckdb

# Analyze immediately
ytchat analyze --db-type duckdb
```

### Workflow 3: Incremental Daily Updates

Set up a scheduled task for daily updates:

```bash
# Download new videos only (stops at first already-downloaded video)
ytchat download @channel1 --stop-on-existing
ytchat download @channel2 --stop-on-existing
ytchat download @channel3 --stop-on-existing
```

### Workflow 4: Batch Processing

Process multiple channels with different settings:

```bash
#!/bin/bash
# download_all.sh

CHANNELS=("@channel1" "@channel2" "@channel3")

for channel in "${CHANNELS[@]}"; do
    echo "Processing $channel..."

    # Download to JSON
    ytchat download "$channel" \
        --start-date 2024-01-01 \
        --stop-on-existing \
        --json-dir "data/json/${channel//[@\/]/_}/"

    # Import to separate database
    # (you can batch import JSON files later)
done
```

### Database Selection Guide

**Use SQLite when:**
- General-purpose storage
- ACID compliance is important
- Moderate dataset sizes (< millions of messages)
- Simple queries and exports

**Use DuckDB when:**
- Analytical workloads (aggregations, GROUP BY)
- Large datasets (millions+ messages)
- Complex queries with joins
- Column-oriented operations

### Data Analysis Examples

**Using JSON files directly:**
```python
import json
import pandas as pd

# Load a JSON file
with open('data/json_exports/20251004_abc123.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data['chat_messages'])
print(f"Total messages: {len(df)}")
print(f"Top chatters:\n{df['author_name'].value_counts().head(10)}")
```

**Using SQLite database:**
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

**Using DuckDB for analytics:**
```python
import duckdb

# Connect to DuckDB
conn = duckdb.connect('data/youtube_chat.duckdb')

# Fast aggregation queries
result = conn.execute("""
    SELECT
        v.channel_name,
        COUNT(DISTINCT cm.author_id) as unique_chatters,
        COUNT(*) as total_messages,
        SUM(CASE WHEN cm.superchat_amount > 0 THEN cm.superchat_amount ELSE 0 END) as total_superchats
    FROM chat_messages cm
    JOIN videos v ON cm.video_id = v.video_id
    GROUP BY v.channel_name
    ORDER BY total_messages DESC
""").fetchdf()

print(result)
```

## Troubleshooting

### Bot Detection / "Sign in to confirm you're not a bot"

If you encounter this error:
```
ERROR: [youtube] Sign in to confirm you're not a bot. Use --cookies-from-browser or --cookies for the authentication.
```

**Solution: Export and use cookies from your browser**

1. **Export cookies using a browser extension:**
   - Chrome/Edge: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. **Visit YouTube while logged in** to your Google account

3. **Export cookies** for `www.youtube.com` in Netscape format (save as `www.youtube.com_cookies.txt`)

4. **Use the cookies file:**
   ```bash
   ytchat download @channelname --cookies www.youtube.com_cookies.txt
   ```

**Important notes:**
- Keep your cookies file secure (it contains your login credentials)
- Add `*.txt` to `.gitignore` to avoid accidentally committing cookies
- Cookies may expire after some time; re-export if needed
- See [yt-dlp FAQ](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp) for more details

### Channel not found
- Make sure the channel ID is correct (try with `@` prefix or without)
- Try using `ytchat validate @channelname` to check
- Use `--search-mode` flag if direct channel access fails
- If still failing, try with `--cookies` option

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
