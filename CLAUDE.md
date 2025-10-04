# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube Chat Downloader is a Python tool for downloading and analyzing YouTube live stream chat history. It uses yt-dlp for video metadata and chat-downloader for chat messages, with support for both SQLite and DuckDB databases via SQLAlchemy. **By default, data is saved to JSON files only**, with optional database storage.

## Development Environment

**Package Manager**: This project uses `uv` (fast Python package manager)

**Python Version**: >=3.9 (configured in `.python-version`)

**Key Dependencies**:
- yt-dlp: YouTube video metadata extraction
- chat-downloader: Chat message extraction
- SQLAlchemy: Database ORM
- Click: CLI framework
- Rich: Terminal output formatting
- Pandas: Data analysis

## Common Commands

### Setup
```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --dev

# Activate virtual environment
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
```

### Running the Application

The CLI is run via Python module (pyproject.toml defines entry point but direct module execution works reliably):

```bash
# Basic usage (after activating venv)
python -m youtube_chat_downloader.cli.commands <command> [options]

# Or use launcher scripts
# Windows: ytchat.bat <command> [options]
# Linux/Mac: ./ytchat.sh <command> [options]
```

**Available commands:**
```bash
# Download (default: JSON only, no database)
python -m youtube_chat_downloader.cli.commands download @channel \
    [--max-videos N] \
    [--db-path PATH] \
    [--db-type sqlite|duckdb] \
    [--json-dir PATH] \
    [--save-to-db / --no-save-to-db] \
    [--search-mode] \
    [--skip-existing / --no-skip-existing] \
    [--stop-on-existing / --no-stop-on-existing] \
    [--start-date YYYY-MM-DD] \
    [--end-date YYYY-MM-DD] \
    [--start-index N] \
    [--end-index N] \
    [--cookies PATH]

# Import JSON to database
python -m youtube_chat_downloader.cli.commands import-json FILE.json \
    [--db-path PATH] \
    [--db-type sqlite|duckdb]

# Validate channel
python -m youtube_chat_downloader.cli.commands validate @channel \
    [--db-type sqlite|duckdb] \
    [--cookies PATH]

# Analyze data
python -m youtube_chat_downloader.cli.commands analyze \
    [--db-path PATH] \
    [--db-type sqlite|duckdb]

# Export to CSV
python -m youtube_chat_downloader.cli.commands export \
    [--db-path PATH] \
    [--db-type sqlite|duckdb] \
    [--video-id ID] \
    [--output FILE]

# List videos in database
python -m youtube_chat_downloader.cli.commands list-videos \
    [--db-path PATH] \
    [--db-type sqlite|duckdb]
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/unit/test_downloader.py
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

## Architecture

### Module Structure

**src/youtube_chat_downloader/**
- `cli/commands.py`: Click-based CLI commands (download, validate, analyze, export)
- `core/downloader.py`: Main YouTubeChatDownloader class for fetching videos and chat
- `core/analyzer.py`: ChatAnalyzer class for querying and analyzing stored data
- `database/models.py`: SQLAlchemy models (Video, ChatMessage)
- `database/connection.py`: DatabaseManager singleton for session management
- `utils/logger.py`: Logging configuration

### Data Flow

1. **Video Discovery**: YouTubeChatDownloader uses yt-dlp to find livestreams from a channel
   - Tries multiple URL patterns: @username, /c/, /user/, /channel/UC*
   - Falls back to search mode if direct channel access fails
   - Filters for videos with livestream indicators

2. **Chat Download**: For each video, chat-downloader fetches messages
   - Fetches ALL available messages (no limit)
   - Extracts: author, message, timestamp, superchats, badges
   - Rate limits with 2-second delays between videos

3. **JSON Export**: Chat messages are first saved to JSON files
   - Files named by date: `YYYYMMDD_videoID.json`
   - Contains video_info, chat_messages, and export_metadata
   - Default location: `data/json_exports/`
   - Provides backup and enables custom processing

4. **Database Storage** (OPTIONAL): SQLAlchemy ORM stores data in SQLite or DuckDB
   - **Default behavior**: Data is saved to JSON only (no database)
   - Use `--save-to-db` flag to enable database storage
   - Supports both SQLite and DuckDB via `--db-type` parameter
   - Video table: extensive metadata including livestream details
   - ChatMessage table: individual messages with foreign key to video_id
   - Uses session.merge() for videos to handle duplicates
   - Handles IntegrityError for duplicate messages

5. **JSON Import**: Import previously downloaded JSON files to database
   - Use `import-json` command to load JSON files into database
   - Useful for selective database imports after batch JSON downloads

6. **Analysis**: ChatAnalyzer provides pandas DataFrames for queries
   - Get chat by video, top chatters, statistics
   - Export to CSV with JOIN between videos and messages

### Database Schema

**videos table**:
- video_id (PK): YouTube video ID
- title, upload_date (indexed), duration, view_count (indexed)
- channel_id (indexed), channel_name, description
- is_live, was_live (indexed): boolean flags
- live_start_timestamp (indexed), live_end_timestamp, release_timestamp: timestamps
- thumbnail: URL to video thumbnail
- categories, tags: JSON arrays
- like_count, comment_count: engagement metrics
- live_status (indexed), availability: video status
- uploader, uploader_id: uploader information
- created_at: timestamp

**Indexes on videos table**:
- `upload_date`, `channel_id`: Original indexes
- `was_live`, `live_status`, `live_start_timestamp`, `view_count`: Additional indexes for query optimization

**chat_messages table**:
- id (PK, autoincrement)
- video_id (indexed): references video
- message_id (unique, indexed): chat message identifier
- author_name (indexed), author_id (indexed), message
- timestamp_usec (indexed): microsecond timestamp
- message_type (indexed): text_message, superchat, etc.
- superchat_amount, superchat_currency
- badges: JSON string of author badges
- created_at: timestamp

**Composite indexes on chat_messages table**:
- `(video_id, timestamp_usec)`: Optimized for fetching messages by video in chronological order
- `(author_id, video_id)`: Optimized for querying user activity across videos
- `(message_type, video_id)`: Optimized for filtering by message type (e.g., superchats)

### Channel ID Handling

The downloader handles multiple channel URL formats:
- `@username` format (modern YouTube)
- `/c/channelname` (custom URLs)
- `/user/username` (legacy)
- `/channel/UC*` (direct channel ID)

When downloading, the code:
1. Strips @ prefix from input
2. Calls `_get_channel_info()` to resolve to real channel_id
3. Tries /streams then /videos tabs
4. Falls back to search with multilingual keywords (直播, live, 실시간)

### Error Handling

- **Incremental downloads**: Checks if video_id already has messages before processing
- **Graceful failures**: Continues processing other videos if one fails
- **Rich console output**: Color-coded status messages (green=success, yellow=warning, red=error)
- **Logging**: Structured logging via utils/logger.py

## Database Support

**Supported databases**:
- **SQLite** (default): `data/youtube_chat.db`
  - Optimized with WAL mode and NORMAL synchronous mode
  - Suitable for most use cases
- **DuckDB**: `data/youtube_chat.duckdb`
  - Excellent for analytical queries
  - Better performance on large datasets

**Configuration**:
- Use `--db-type sqlite` or `--db-type duckdb` to select database
- Override default path with `--db-path` flag
- All indexes are created automatically on initialization

## Important Notes

- The CLI entry point is `ytchat` (defined in pyproject.toml [project.scripts])
- Direct module execution is more reliable: `python -m youtube_chat_downloader.cli.commands`
- Launcher scripts provided: `ytchat.bat` (Windows) and `ytchat.sh` (Linux/Mac)
- There's a `main.py` in the root directory that appears to be a legacy entry point
- Search mode uses multilingual keywords to handle international channels (直播, live, 실시간, ライブ)
- **No message limit**: Downloads ALL available messages for each video
- Database path defaults to `data/youtube_chat.db`
- JSON exports default to `data/json_exports/` directory
- **Cookies support**: Use `--cookies` to provide authentication cookies in Netscape format to bypass bot detection

## Key Features Implemented

### JSON-First Architecture (NEW)
- **Default behavior**: Downloads save to JSON only (no database)
- Use `--save-to-db` flag to enable database storage
- JSON files serve as the primary data format
- Filename format: `YYYYMMDD_videoID.json` (based on upload date)
- Contains complete video metadata and all chat messages
- Provides backup and enables custom data processing
- Use `--json-dir PATH` to specify custom export directory
- Default location: `data/json_exports/`

### Flexible Database Backend (NEW)
- Support for both SQLite and DuckDB
- SQLite optimized with WAL mode and pragma settings
- Comprehensive indexing strategy:
  - Single-column indexes on frequently queried fields
  - Composite indexes for common query patterns
  - All indexes created automatically on database initialization
- Use `--db-type` to switch between database backends

### Extended Video Metadata (NEW)
- Stores comprehensive livestream information including:
  - Livestream timestamps (start, end, release)
  - Thumbnail URLs
  - Categories and tags (JSON format)
  - Engagement metrics (likes, comments)
  - Livestream status and availability
  - Uploader information
- Run `python scripts/migrate_add_video_details.py` to upgrade existing databases

### Unlimited Message Download (NEW)
- Removed 10,000 message limit per video
- Downloads ALL available chat messages
- Suitable for very active livestream chats

### JSON to Database Import (NEW)
- New `import-json` command for importing JSON files to database
- Checks for existing data before import
- Supports batch processing of downloaded JSON files
- Works with both SQLite and DuckDB

### Incremental Download
- `--skip-existing` flag (default: True) checks database for existing messages
- `--no-skip-existing` to force re-download
- `--stop-on-existing` (default: True) stops entirely when encountering first already-downloaded video (useful for incremental updates since videos are processed newest-first)
- `--no-stop-on-existing` to continue processing all videos even if some are already downloaded
- Significantly reduces redundant downloads

### Date Range Filtering
- `--start-date` and `--end-date` in YYYY-MM-DD format
- Filters videos by upload_date field
- Useful for historical data collection

### Index Range Filtering
- `--start-index` and `--end-index` for batch processing
- 0-based indexing, end-index is exclusive
- Ideal for splitting large channel downloads

### Filter Execution Order
1. Fetch all livestreams from channel
2. Apply date range filter (if specified)
3. Apply index range filter (if specified)
4. Apply max-videos limit (if specified)
5. Execute download with incremental check
6. Save to JSON file first, then optionally to database (if `--save-to-db` is specified)

## Workflow Examples

### Recommended Workflow: JSON-First

```bash
# Step 1: Download to JSON only (default)
python -m youtube_chat_downloader.cli.commands download @channel --max-videos 100

# Step 2: Inspect/process JSON files as needed
# Files are in data/json_exports/YYYYMMDD_videoID.json

# Step 3: Import selected JSON files to SQLite database
python -m youtube_chat_downloader.cli.commands import-json data/json_exports/20251004_abc123.json

# Step 4: Or import to DuckDB for analytics
python -m youtube_chat_downloader.cli.commands import-json data/json_exports/20251004_abc123.json --db-type duckdb
```

### Alternative: Direct to Database

```bash
# Download directly to database (SQLite)
python -m youtube_chat_downloader.cli.commands download @channel --save-to-db

# Download directly to DuckDB
python -m youtube_chat_downloader.cli.commands download @channel --save-to-db --db-type duckdb
```

### Database Selection Guide

**Use SQLite when**:
- General-purpose storage
- ACID compliance is important
- Moderate dataset sizes (< millions of messages)
- Simple queries and exports

**Use DuckDB when**:
- Analytical workloads (aggregations, GROUP BY)
- Large datasets (millions+ messages)
- Complex queries with joins
- Column-oriented operations

## Examples Directory

See `examples/example_usage.py` for Python API usage examples, including:
- Programmatic download
- Channel validation
- Data analysis
- CSV export
- Single video download
