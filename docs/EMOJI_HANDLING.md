# YouTube Chat Emoji Handling

This document explains how emojis in YouTube chat are stored and processed.

## Overview

YouTube chat contains **two types of emojis**:

### 1. Standard Unicode Emojis (😊, 👍, ❤️)

**Storage**: Stored directly as Unicode characters in the `message` field.

- SQLite with UTF-8 encoding natively supports Unicode
- Python 3 strings are Unicode by default
- **No conversion needed** - emojis are stored as-is
- Examples: 😊, 👍, ❤️, 🔥, 🎉

**How it works**:
```python
message = "Hello 😊 world!"  # Stored exactly like this in database
# Retrieved as: "Hello 😊 world!"
```

### 2. YouTube Custom Emojis (Channel Member/Subscriber Emojis)

**Storage**: Stored as metadata in the `emotes` field (JSON).

- These are custom images specific to the channel
- Displayed as `:emoji_name:` in message text (e.g., `:face-blue-smiling:`)
- Full image URL and metadata stored in separate `emotes` field
- Examples: Channel badges, membership perks, custom stickers

**How it works**:
```python
# Message text
message = "Hello :face-blue-smiling: world!"

# Emotes metadata (JSON in 'emotes' field)
emotes = [
  {
    "name": "face-blue-smiling",
    "url": "https://yt3.ggpht.com/...",
    "id": "UCxxxxxx/emoji_id"
  }
]
```

## Data Structure

### Database Storage

The `chat_messages` table has an `emotes` field (TEXT/JSON) that stores emoji information:

```json
[
  {
    "name": "face-blue-smiling",
    "id": "UCxxxxxx/emoji_id",
    "url": "https://yt3.ggpht.com/...",
    "is_custom_emoji": true
  }
]
```

### Fields

- **name**: The emoji identifier (e.g., `face-blue-smiling`)
- **id**: YouTube's internal emoji ID
- **url**: Direct URL to the emoji image
- **is_custom_emoji**: Boolean indicating if it's a custom channel emoji

## Usage Examples

### 1. Working with Unicode Emojis

```python
from youtube_chat_downloader.utils.emoji_handler import (
    has_unicode_emojis,
    extract_unicode_emojis
)

# Check if message has Unicode emojis
message = "Hello 😊 world 🔥"
if has_unicode_emojis(message):
    emojis = extract_unicode_emojis(message)
    print(emojis)  # ['😊', '🔥']

# Unicode emojis are already in the message - no conversion needed!
print(message)  # "Hello 😊 world 🔥"
```

### 2. Working with Custom Emojis

```python
from youtube_chat_downloader.utils.emoji_handler import extract_emote_info

# From database
emotes_json = '[{"name": "face-blue-smiling", "url": "https://..."}]'
emotes = extract_emote_info(emotes_json)

for emote in emotes:
    print(f"Emoji: {emote['name']}")
    print(f"URL: {emote['url']}")
```

### 3. Handling Both Types Together

```python
from youtube_chat_downloader.utils.emoji_handler import get_all_emojis

message = "Hello 😊 and :custom-face: together!"
emotes_json = '[{"name": "custom-face", "url": "https://..."}]'

all_emojis = get_all_emojis(message, emotes_json)
print(all_emojis['unicode'])   # ['😊']
print(all_emojis['custom'])    # [{'name': 'custom-face', ...}]
```

### 4. Format Custom Emojis for Display

```python
from youtube_chat_downloader.utils.emoji_handler import (
    format_message_with_emotes,
    reconstruct_full_message
)

message = "Hello 😊 and :face-blue-smiling: together!"
emotes_json = '[{"name": "face-blue-smiling", "url": "https://..."}]'

# Format custom emojis as text
formatted = format_message_with_emotes(message, emotes_json)
# Output: "Hello 😊 and [Emoji: face-blue-smiling] together!"

# Or mark custom emojis as image placeholders
reconstructed = reconstruct_full_message(message, emotes_json)
# Output: "Hello 😊 and [IMG:face-blue-smiling] together!"
```

### 5. Convert to Markdown

```python
from youtube_chat_downloader.utils.emoji_handler import emotes_to_markdown

emotes_json = '...'
markdown = emotes_to_markdown(emotes_json)
# Output: "![face-blue-smiling](https://yt3.ggpht.com/...)"
```

### 6. Analyze Emoji Usage

```python
from youtube_chat_downloader.core.analyzer import ChatAnalyzer
from youtube_chat_downloader.utils.emoji_handler import (
    get_emote_names,
    extract_unicode_emojis,
    has_unicode_emojis
)
from collections import Counter

analyzer = ChatAnalyzer()
df = analyzer.get_chat_by_video('VIDEO_ID')

# Analyze Unicode emojis
unicode_emojis = []
for message in df['message']:
    if has_unicode_emojis(message):
        unicode_emojis.extend(extract_unicode_emojis(message))

unicode_counts = Counter(unicode_emojis)
print("Top Unicode emojis:", unicode_counts.most_common(10))

# Analyze custom emojis
custom_emojis = []
for emotes_data in df[df['emotes'].notna()]['emotes']:
    custom_emojis.extend(get_emote_names(emotes_data))

custom_counts = Counter(custom_emojis)
print("Top custom emojis:", custom_counts.most_common(10))
```

## Working with JSON Exports

When messages are exported to JSON files, the emoji data is preserved:

```json
{
  "video_info": {...},
  "chat_messages": [
    {
      "message": "Great stream :face-blue-smiling:",
      "emotes": [
        {
          "name": "face-blue-smiling",
          "url": "https://yt3.ggpht.com/..."
        }
      ]
    }
  ]
}
```

You can process these files to:
1. Display emojis as images in a web viewer
2. Replace emoji codes with actual images
3. Analyze emoji sentiment
4. Track emoji usage patterns

## Utility Functions

The `emoji_handler` module provides these functions:

| Function | Description |
|----------|-------------|
| `extract_emote_info()` | Parse JSON and extract emoji objects |
| `format_message_with_emotes()` | Replace `:emoji:` with readable text |
| `emotes_to_markdown()` | Convert to Markdown image syntax |
| `get_emote_names()` | Extract list of emoji names |
| `count_emotes()` | Count emojis in a message |
| `has_custom_emojis()` | Check if message contains `:emoji:` syntax |

## Migration

If you have an existing database, add the `emotes` field:

```bash
python scripts/migrate_add_emotes.py --db-path data/youtube_chat.db
```

## Example Script

See `examples/emoji_usage.py` for a complete example:

```bash
python examples/emoji_usage.py VIDEO_ID
```

This will:
- Show emoji usage statistics
- Display sample messages with emojis
- List the most popular emojis
- Export messages to a text file

## Debugging Emoji Data

To inspect the raw message structure from chat-downloader:

```bash
python scripts/inspect_message_structure.py VIDEO_ID
```

This displays the first 5 messages with full JSON structure, helping you understand the emoji format for that specific video.

## Common Patterns

### Pattern 1: Finding Messages with Specific Emoji

```python
df = analyzer.get_chat_by_video('VIDEO_ID')

for _, row in df.iterrows():
    if row['emotes']:
        emoji_names = get_emote_names(row['emotes'])
        if 'face-blue-smiling' in emoji_names:
            print(f"{row['author_name']}: {row['message']}")
```

### Pattern 2: Export Emoji Images

```python
emotes = extract_emote_info(emotes_json)
for emote in emotes:
    url = emote.get('url')
    if url:
        # Download image
        import requests
        img_data = requests.get(url).content
        with open(f"{emote['name']}.png", 'wb') as f:
            f.write(img_data)
```

### Pattern 3: Replace with Unicode/Images in HTML

```python
def emojis_to_html(message, emotes_json):
    emotes = extract_emote_info(emotes_json)
    html = message
    for emote in emotes:
        name = emote['name']
        url = emote.get('url', '')
        if url:
            img_tag = f'<img src="{url}" alt="{name}" class="emoji" />'
            html = html.replace(f':{name}:', img_tag)
    return html
```

## Important: Unicode Emoji Storage in SQLite

### How It Works

**SQLite automatically handles Unicode emojis correctly:**

1. **UTF-8 Encoding**: SQLite stores text as UTF-8 by default
2. **Python 3 Unicode**: Python 3 strings are Unicode by default
3. **No Conversion Needed**: Emojis like 😊, 🔥, ❤️ are stored and retrieved as-is
4. **Multi-byte Characters**: Emojis are multi-byte UTF-8 sequences (e.g., 😊 = 4 bytes)

### Verification

Run the test script to verify emoji storage:

```bash
python scripts/test_emoji_storage.py
```

This will:
- Create a test database with emoji messages
- Store and retrieve Unicode emojis
- Verify that emojis are preserved correctly
- Test emoji extraction functions

### Example Output

```python
# Stored in database
message = "Hello 😊 world 🔥"

# Retrieved from database (identical)
retrieved = "Hello 😊 world 🔥"

# Extract emojis
emojis = extract_unicode_emojis(retrieved)
# Result: ['😊', '🔥']
```

### Why No Conversion Is Needed

**Shortcodes vs Unicode**:
- ❌ Wrong: Storing `:smile:` and converting to 😊
- ✅ Correct: Storing 😊 directly as UTF-8

YouTube chat-downloader already provides Unicode emojis in the message text. We simply store them as-is.

### Custom Emojis Are Different

**Custom YouTube emojis** (`:face-blue-smiling:`) are **NOT Unicode**:
- They are channel-specific images
- They don't have Unicode codepoints
- They must be stored as metadata (image URLs)
- The text `:emoji_name:` is just a placeholder

## Notes

- YouTube custom emojis are channel-specific (member badges, subscriber emojis)
- Standard Unicode emojis (😊, 👍) are stored as regular text in the `message` field
- The `emotes` field only contains YouTube's custom emoji metadata
- Emoji URLs may expire or change over time
- SQLite TEXT columns with UTF-8 encoding natively support Unicode emojis
- No special encoding/decoding is required in Python 3
