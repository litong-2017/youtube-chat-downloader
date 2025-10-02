@echo off
REM YouTube Chat Downloader launcher for Windows
REM Usage: ytchat.bat <command> [options]

REM Activate virtual environment and run the CLI
call .venv\Scripts\activate.bat
python -m youtube_chat_downloader.cli.commands %*
