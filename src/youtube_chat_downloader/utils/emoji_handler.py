"""
Emoji and emote handling utilities for YouTube chat messages.

YouTube chat contains two types of emojis:
1. Standard Unicode emojis (😊, 👍, ❤️) - stored directly as Unicode in message text
2. Custom YouTube emojis (channel member emojis) - stored as image URLs in emotes field

This module handles both types:
- Unicode emojis are already properly stored in SQLite as UTF-8 text
- Custom emojis need special handling to reconstruct from metadata

Note: SQLite with UTF-8 encoding natively supports Unicode emojis.
Python 3 strings are Unicode by default, so no conversion is needed.
"""

import json
import re
from typing import Dict, List, Optional, Tuple


def extract_emote_info(emotes_data: Optional[str]) -> List[Dict]:
    """
    Extract emote information from JSON string.

    Args:
        emotes_data: JSON string containing emote information

    Returns:
        List of emote dictionaries with name, id, and url fields
    """
    if not emotes_data:
        return []

    try:
        emotes = json.loads(emotes_data)
        if not isinstance(emotes, list):
            return []

        result = []
        for emote in emotes:
            if isinstance(emote, dict):
                result.append({
                    'name': emote.get('name', ''),
                    'id': emote.get('id', emote.get('emoji_id', '')),
                    'url': emote.get('url', emote.get('image', {}).get('url', '')),
                    'is_custom_emoji': emote.get('is_custom_emoji', True)
                })
        return result
    except (json.JSONDecodeError, Exception):
        return []


def format_message_with_emotes(message: str, emotes_data: Optional[str]) -> str:
    """
    Replace emote placeholders in message with readable format.

    Converts :emoji_name: format to [Emoji: emoji_name] for better readability.

    Args:
        message: The chat message text
        emotes_data: JSON string containing emote information

    Returns:
        Message with emotes formatted for display
    """
    if not message or not emotes_data:
        return message

    emotes = extract_emote_info(emotes_data)
    if not emotes:
        return message

    # Replace :emoji_name: with [Emoji: emoji_name]
    formatted = message
    for emote in emotes:
        emote_name = emote.get('name', '')
        if emote_name:
            # Match :emoji_name: pattern
            pattern = f":{re.escape(emote_name)}:"
            replacement = f"[Emoji: {emote_name}]"
            formatted = re.sub(pattern, replacement, formatted)

    return formatted


def emotes_to_markdown(emotes_data: Optional[str]) -> str:
    """
    Convert emotes to markdown image format.

    Args:
        emotes_data: JSON string containing emote information

    Returns:
        Markdown formatted string with emote images
    """
    emotes = extract_emote_info(emotes_data)
    if not emotes:
        return ""

    markdown_parts = []
    for emote in emotes:
        name = emote.get('name', 'emoji')
        url = emote.get('url', '')
        if url:
            markdown_parts.append(f"![{name}]({url})")
        else:
            markdown_parts.append(f":{name}:")

    return " ".join(markdown_parts)


def get_emote_names(emotes_data: Optional[str]) -> List[str]:
    """
    Extract just the emote names from emotes data.

    Args:
        emotes_data: JSON string containing emote information

    Returns:
        List of emote names
    """
    emotes = extract_emote_info(emotes_data)
    return [emote.get('name', '') for emote in emotes if emote.get('name')]


def count_emotes(emotes_data: Optional[str]) -> int:
    """
    Count the number of emotes in a message.

    Args:
        emotes_data: JSON string containing emote information

    Returns:
        Number of emotes
    """
    return len(extract_emote_info(emotes_data))


def has_custom_emojis(message: str) -> bool:
    """
    Check if a message contains custom emoji syntax (:emoji_name:).

    Args:
        message: The chat message text

    Returns:
        True if message contains :emoji_name: patterns
    """
    if not message:
        return False

    # Pattern to match :word: but exclude common timestamps like 1:30
    pattern = r':[a-zA-Z][a-zA-Z0-9_-]*:'
    return bool(re.search(pattern, message))


def has_unicode_emojis(message: str) -> bool:
    """
    Check if a message contains Unicode emoji characters.

    Args:
        message: The chat message text

    Returns:
        True if message contains Unicode emojis
    """
    if not message:
        return False

    # Unicode emoji ranges (main blocks)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # extended symbols
        "]+",
        flags=re.UNICODE
    )
    return bool(emoji_pattern.search(message))


def extract_unicode_emojis(message: str) -> List[str]:
    """
    Extract all Unicode emojis from a message.

    Args:
        message: The chat message text

    Returns:
        List of Unicode emoji characters found
    """
    if not message:
        return []

    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.findall(message)


def get_all_emojis(message: str, emotes_data: Optional[str] = None) -> Dict[str, List]:
    """
    Get both Unicode and custom emojis from a message.

    Args:
        message: The chat message text
        emotes_data: JSON string containing custom emote information

    Returns:
        Dictionary with 'unicode' and 'custom' emoji lists
    """
    return {
        'unicode': extract_unicode_emojis(message),
        'custom': extract_emote_info(emotes_data) if emotes_data else []
    }


def reconstruct_full_message(message: str, emotes_data: Optional[str]) -> str:
    """
    Reconstruct message with custom emojis replaced by image placeholders.

    This is useful for display purposes where you want to show both:
    - Unicode emojis as-is (😊)
    - Custom emojis as [IMG:emoji_name]

    Args:
        message: The chat message text
        emotes_data: JSON string containing custom emote information

    Returns:
        Message with custom emojis marked
    """
    if not message:
        return message

    # Unicode emojis are already in the message text
    result = message

    # Replace custom emoji placeholders
    if emotes_data:
        emotes = extract_emote_info(emotes_data)
        for emote in emotes:
            name = emote.get('name', '')
            if name:
                # Replace :emoji_name: with [IMG:emoji_name]
                pattern = f":{re.escape(name)}:"
                result = re.sub(pattern, f"[IMG:{name}]", result)

    return result
