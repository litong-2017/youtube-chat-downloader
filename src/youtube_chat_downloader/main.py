"""Main entry point for the application."""

import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from youtube_chat_downloader.cli.commands import cli

if __name__ == "__main__":
    cli()
