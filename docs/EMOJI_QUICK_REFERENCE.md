# Emoji Handling - Quick Reference

## Two Types of Emojis in YouTube Chat

| Type | Example | Storage | Location |
|------|---------|---------|----------|
| **Unicode Emojis** | 😊 👍 ❤️ 🔥 | UTF-8 characters | `message` field |
| **Custom Emojis** | :face-blue-smiling: | JSON metadata | `emotes` field |

## Unicode Emojis (😊, 👍, ❤️)

### Storage
```python
# Stored directly in message field as UTF-8
message = "Hello 😊 world 🔥"
# ↑ Stored exactly like this in SQLite
```

### Key Points
- ✅ **No conversion needed**
- ✅ SQLite stores as UTF-8 by default
- ✅ Python 3 strings are Unicode by default
- ✅ Retrieved exactly as stored

### Working with Unicode Emojis

```python
from youtube_chat_downloader.utils.emoji_handler import (
    has_unicode_emojis,
    extract_unicode_emojis
)

message = "Hello 😊 world 🔥"

# Check if message has emojis
has_unicode_emojis(message)  # True

# Extract emoji list
extract_unicode_emojis(message)  # ['😊', '🔥']
```

## Custom Emojis (:emoji_name:)

### Storage
```python
# Message text (placeholder)
message = "Hello :face-blue-smiling: world"

# Metadata stored in emotes field (JSON)
emotes = [
  {
    "name": "face-blue-smiling",
    "url": "https://yt3.ggpht.com/...",
    "id": "UC.../emoji_id"
  }
]
```

### Key Points
- 📷 These are **images**, not Unicode characters
- 🎨 Channel-specific (member/subscriber emojis)
- 🔗 Image URL stored in separate field
- 📝 `:emoji_name:` is just a text placeholder

### Working with Custom Emojis

```python
from youtube_chat_downloader.utils.emoji_handler import (
    extract_emote_info,
    format_message_with_emotes
)

emotes_json = '[{"name": "face-blue-smiling", "url": "https://..."}]'

# Extract emoji metadata
emotes = extract_emote_info(emotes_json)
# [{'name': 'face-blue-smiling', 'url': 'https://...', ...}]

# Format message for display
message = "Hello :face-blue-smiling: world"
formatted = format_message_with_emotes(message, emotes_json)
# "Hello [Emoji: face-blue-smiling] world"
```

## Common Tasks

### 1. Check Both Emoji Types

```python
from youtube_chat_downloader.utils.emoji_handler import get_all_emojis

message = "Hello 😊 and :custom-emoji: together!"
emotes_json = '...'

all_emojis = get_all_emojis(message, emotes_json)
print(all_emojis['unicode'])   # ['😊']
print(all_emojis['custom'])    # [{'name': 'custom-emoji', ...}]
```

### 2. Count Emoji Usage

```python
from youtube_chat_downloader.core.analyzer import ChatAnalyzer
from youtube_chat_downloader.utils.emoji_handler import extract_unicode_emojis
from collections import Counter

analyzer = ChatAnalyzer()
df = analyzer.get_chat_by_video('VIDEO_ID')

# Count Unicode emojis
all_unicode = []
for msg in df['message']:
    all_unicode.extend(extract_unicode_emojis(msg))

Counter(all_unicode).most_common(10)
```

### 3. Filter Messages with Emojis

```python
# Unicode emojis
df_unicode = df[df['message'].apply(has_unicode_emojis)]

# Custom emojis
df_custom = df[df['emotes'].notna()]
```

### 4. Export Custom Emoji Images

```python
import requests

emotes = extract_emote_info(emotes_json)
for emote in emotes:
    url = emote.get('url')
    if url:
        img = requests.get(url).content
        with open(f"{emote['name']}.png", 'wb') as f:
            f.write(img)
```

## Database Schema

```sql
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    message TEXT,              -- Contains Unicode emojis directly: "Hello 😊"
    emotes TEXT,               -- JSON: [{"name": "...", "url": "..."}]
    -- other fields...
);
```

## Testing

```bash
# Verify Unicode emoji storage works correctly
python scripts/test_emoji_storage.py

# Inspect raw message structure
python scripts/inspect_message_structure.py VIDEO_ID

# Analyze emoji usage in a video
python examples/emoji_usage.py VIDEO_ID
```

## Migration

Add `emotes` field to existing database:

```bash
python scripts/migrate_add_emotes.py --db-path data/youtube_chat.db
```

## FAQ

**Q: Why not store Unicode emojis as `:smile:` shortcodes?**
A: YouTube chat-downloader already provides Unicode emojis (😊) in the message text. No conversion needed!

**Q: Can I convert custom emojis to Unicode?**
A: No. Custom emojis are channel-specific images, not Unicode characters.

**Q: Will Unicode emojis work in all environments?**
A: Yes. SQLite with UTF-8 and Python 3 handle Unicode natively.

**Q: What about emoji modifiers (skin tones)?**
A: They're stored as multi-codepoint sequences and handled correctly by UTF-8.

## Utility Functions

| Function | Purpose |
|----------|---------|
| `has_unicode_emojis()` | Check if message has Unicode emojis |
| `extract_unicode_emojis()` | Get list of Unicode emojis |
| `has_custom_emojis()` | Check for `:emoji_name:` syntax |
| `extract_emote_info()` | Parse custom emoji metadata |
| `get_all_emojis()` | Get both Unicode and custom |
| `format_message_with_emotes()` | Format custom emojis as text |
| `reconstruct_full_message()` | Mark custom emojis as [IMG:...] |

## See Also

- Full documentation: `docs/EMOJI_HANDLING.md`
- Example code: `examples/emoji_usage.py`
- Test script: `scripts/test_emoji_storage.py`
