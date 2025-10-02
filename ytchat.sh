#!/bin/bash
# YouTube Chat Downloader launcher for Linux/Mac
# Usage: ./ytchat.sh <command> [options]

# Activate virtual environment and run the CLI
source .venv/bin/activate
python -m youtube_chat_downloader.cli.commands "$@"
