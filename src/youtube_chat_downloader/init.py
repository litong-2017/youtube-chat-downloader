"""YouTube Chat Downloader - A tool to download YouTube live chat history."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.downloader import YouTubeChatDownloader
from .core.analyzer import ChatAnalyzer

__all__ = ["YouTubeChatDownloader", "ChatAnalyzer"]
