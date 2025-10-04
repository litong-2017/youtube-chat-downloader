"""Command line interface."""

import click
from rich.console import Console
from rich.table import Table

from ..core.analyzer import ChatAnalyzer
from ..core.downloader import YouTubeChatDownloader

console = Console()


@click.group()
def cli():
    """YouTube Chat Downloader CLI."""
    pass


@cli.command()
@click.argument('channel_id')
@click.option('--max-videos', '-m', type=int, help='Maximum number of videos to process')
@click.option('--db-path', '-d', help='Database file path (default: data/youtube_chat.db or data/youtube_chat.duckdb)')
@click.option('--db-type', type=click.Choice(['sqlite', 'duckdb'], case_sensitive=False), default='sqlite', help='Database type (default: sqlite)')
@click.option('--json-dir', '-j', default='data/json_exports', help='Directory to save JSON exports')
@click.option('--search-mode', '-s', is_flag=True, help='Use search mode to find videos')
@click.option('--skip-existing/--no-skip-existing', default=True, help='Skip already downloaded videos (incremental mode)')
@click.option('--stop-on-existing/--no-stop-on-existing', default=True, help='Stop when encountering first already-downloaded video (default: enabled)')
@click.option('--start-date', help='Start date for video range (YYYY-MM-DD)')
@click.option('--end-date', help='End date for video range (YYYY-MM-DD)')
@click.option('--start-index', type=int, default=0, help='Start index in video list (0-based)')
@click.option('--end-index', type=int, help='End index in video list (exclusive)')
@click.option('--save-to-db/--no-save-to-db', default=False, help='Save to database (default: only save to JSON)')
@click.option('--cookies', '-c', help='Path to cookies file (Netscape format)')
def download(channel_id: str, max_videos: int, db_path: str, db_type: str, json_dir: str, search_mode: bool,
             skip_existing: bool, stop_on_existing: bool, start_date: str, end_date: str,
             start_index: int, end_index: int, save_to_db: bool, cookies: str):
    """Download chat history for a YouTube channel.

    Examples:
        ytchat download @channelname  # Default: only save to JSON
        ytchat download @channelname --save-to-db  # Save to both JSON and SQLite database
        ytchat download @channelname --save-to-db --db-type duckdb  # Save to DuckDB
        ytchat download @channelname --max-videos 10
        ytchat download @channelname --start-date 2024-01-01 --end-date 2024-12-31
        ytchat download @channelname --start-index 0 --end-index 50
        ytchat download @channelname --no-skip-existing  # Re-download all videos
        ytchat download @channelname --no-stop-on-existing  # Continue processing all videos instead of stopping
        ytchat download @channelname --json-dir custom/path  # Custom JSON export directory
        ytchat download @channelname --cookies cookies.txt  # Use cookies for authentication
    """
    downloader = YouTubeChatDownloader(db_path, json_output_dir=json_dir, db_type=db_type, cookies_file=cookies)

    # 先验证频道是否存在
    console.print(f"[cyan]Validating channel: {channel_id}[/cyan]")
    channel_info = downloader._get_channel_info(channel_id.strip('@'))

    if channel_info:
        console.print(f"[green]✅ Found channel: {channel_info.get('channel_name', 'Unknown')}[/green]")
        console.print(f"[blue]Channel ID: {channel_info.get('channel_id', 'Unknown')}[/blue]")
    else:
        console.print(f"[yellow]⚠️ Could not verify channel, but continuing...[/yellow]")

    if search_mode:
        console.print("[cyan]Using search mode to find livestreams...[/cyan]")

    # 显示过滤选项
    if start_date or end_date:
        console.print(f"[cyan]Date range: {start_date or 'beginning'} to {end_date or 'now'}[/cyan]")
    if end_index is not None:
        console.print(f"[cyan]Index range: {start_index} to {end_index}[/cyan]")
    if stop_on_existing:
        console.print("[cyan]Stop-on-existing mode: Will stop at first already-downloaded video[/cyan]")
    elif skip_existing:
        console.print("[cyan]Incremental mode: Skipping already downloaded videos[/cyan]")

    if save_to_db:
        console.print("[cyan]Saving to both JSON and database[/cyan]")
    else:
        console.print("[cyan]Saving to JSON only (use --save-to-db to also save to database)[/cyan]")

    downloader.download_channel_chat_history(
        channel_id=channel_id,
        max_videos=max_videos,
        skip_existing=skip_existing,
        start_date=start_date,
        end_date=end_date,
        start_index=start_index,
        end_index=end_index,
        stop_on_existing=stop_on_existing,
        save_to_db=save_to_db
    )


@cli.command()
@click.argument('channel_id')
@click.option('--db-type', type=click.Choice(['sqlite', 'duckdb'], case_sensitive=False), default='sqlite', help='Database type (default: sqlite)')
@click.option('--cookies', '-c', help='Path to cookies file (Netscape format)')
def validate(channel_id: str, db_type: str, cookies: str):
    """Validate if a YouTube channel exists and get its info."""
    downloader = YouTubeChatDownloader(db_type=db_type, cookies_file=cookies)
    
    console.print(f"[cyan]Validating channel: {channel_id}[/cyan]")
    channel_info = downloader._get_channel_info(channel_id.strip('@'))
    
    if channel_info:
        table = Table(title="Channel Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Channel Name", channel_info.get('channel_name', 'Unknown'))
        table.add_row("Channel ID", channel_info.get('channel_id', 'Unknown'))
        table.add_row("Channel URL", channel_info.get('channel_url', 'Unknown'))
        
        console.print(table)
        
        # 尝试获取视频
        console.print("[cyan]Checking for livestream videos...[/cyan]")
        videos = downloader.get_channel_livestreams(channel_id)
        console.print(f"Found {len(videos)} potential livestream videos")
        
        if videos:
            video_table = Table(title="Recent Livestreams")
            video_table.add_column("Video ID", style="cyan")
            video_table.add_column("Title", style="white")
            
            for video in videos[:5]:  # 显示前5个
                video_table.add_row(
                    video['video_id'], 
                    video['title'][:50] + "..." if len(video['title']) > 50 else video['title']
                )
            
            console.print(video_table)
    else:
        console.print(f"[red]❌ Could not find or validate channel: {channel_id}[/red]")
        console.print("[yellow]Suggestions:[/yellow]")
        console.print("1. Make sure the channel ID is correct")
        console.print("2. Try using the full channel URL")
        console.print("3. Check if the channel has any livestreams")


@cli.command()
@click.option('--db-path', '-d', help='Database file path (default: data/youtube_chat.db or data/youtube_chat.duckdb)')
@click.option('--db-type', type=click.Choice(['sqlite', 'duckdb'], case_sensitive=False), default='sqlite', help='Database type (default: sqlite)')
def analyze(db_path: str, db_type: str):
    """Analyze downloaded chat data and show statistics."""
    analyzer = ChatAnalyzer(db_path, db_type=db_type)

    console.print("[bold cyan]Database Statistics[/bold cyan]\n")

    try:
        stats = analyzer.get_statistics()

        # 总体统计
        table = Table(title="Overall Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Total Videos", str(stats['video_count']))
        table.add_row("Total Messages", str(stats['message_count']))

        console.print(table)
        console.print()

        # 最活跃视频
        if stats['top_videos']:
            video_table = Table(title="Top Videos by Message Count")
            video_table.add_column("Video ID", style="cyan")
            video_table.add_column("Messages", style="green")

            for video_id, count in stats['top_videos']:
                video_table.add_row(video_id, str(count))

            console.print(video_table)
            console.print()

        # 最活跃用户
        top_chatters = analyzer.get_top_chatters(limit=10)
        if not top_chatters.empty:
            chatter_table = Table(title="Top 10 Most Active Chatters")
            chatter_table.add_column("Username", style="cyan")
            chatter_table.add_column("Message Count", style="green")

            for _, row in top_chatters.iterrows():
                chatter_table.add_row(row['author_name'], str(row['message_count']))

            console.print(chatter_table)

    except Exception as e:
        console.print(f"[red]Error analyzing data: {e}[/red]")


@cli.command()
@click.option('--db-path', '-d', help='Database file path (default: data/youtube_chat.db or data/youtube_chat.duckdb)')
@click.option('--db-type', type=click.Choice(['sqlite', 'duckdb'], case_sensitive=False), default='sqlite', help='Database type (default: sqlite)')
@click.option('--video-id', '-v', help='Export specific video (leave empty for all)')
@click.option('--output', '-o', default='chat_export.csv', help='Output CSV file path')
def export(db_path: str, db_type: str, video_id: str, output: str):
    """Export chat data to CSV format."""
    analyzer = ChatAnalyzer(db_path, db_type=db_type)

    try:
        console.print(f"[cyan]Exporting data to {output}...[/cyan]")
        analyzer.export_to_csv(video_id=video_id, output_file=output)
        console.print(f"[green]✅ Data exported successfully to {output}[/green]")
    except Exception as e:
        console.print(f"[red]Error exporting data: {e}[/red]")


@cli.command()
@click.option('--db-path', '-d', help='Database file path (default: data/youtube_chat.db or data/youtube_chat.duckdb)')
@click.option('--db-type', type=click.Choice(['sqlite', 'duckdb'], case_sensitive=False), default='sqlite', help='Database type (default: sqlite)')
def list_videos(db_path: str, db_type: str):
    """List all downloaded videos in the database."""
    from ..database.connection import DatabaseManager
    from ..database.models import Video, ChatMessage
    from sqlalchemy import func

    db_manager = DatabaseManager(db_path, db_type=db_type)

    try:
        with db_manager.get_session() as session:
            # 查询所有视频及消息数量
            results = session.query(
                Video.video_id,
                Video.title,
                Video.channel_name,
                Video.upload_date,
                func.count(ChatMessage.id).label('message_count')
            ).outerjoin(
                ChatMessage, Video.video_id == ChatMessage.video_id
            ).group_by(
                Video.video_id
            ).order_by(
                Video.upload_date.desc()
            ).all()

            if not results:
                console.print("[yellow]No videos found in database[/yellow]")
                return

            table = Table(title=f"Downloaded Videos ({len(results)} total)")
            table.add_column("Video ID", style="cyan")
            table.add_column("Title", style="white")
            table.add_column("Channel", style="blue")
            table.add_column("Date", style="yellow")
            table.add_column("Messages", style="green")

            for video in results:
                title = video.title[:50] + "..." if video.title and len(video.title) > 50 else (video.title or "N/A")
                table.add_row(
                    video.video_id,
                    title,
                    video.channel_name or "N/A",
                    video.upload_date or "N/A",
                    str(video.message_count)
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing videos: {e}[/red]")


@cli.command()
@click.argument('json_path', type=click.Path(exists=True))
@click.option('--db-path', '-d', help='Database file path (default: data/youtube_chat.db or data/youtube_chat.duckdb)')
@click.option('--db-type', type=click.Choice(['sqlite', 'duckdb'], case_sensitive=False), default='sqlite', help='Database type (default: sqlite)')
def import_json(json_path: str, db_path: str, db_type: str):
    """Import chat data from JSON file to database.

    Examples:
        ytchat import-json data/json_exports/20251004_videoID.json
        ytchat import-json data/json_exports/20251004_videoID.json --db-type duckdb
        ytchat import-json data/json_exports/20251004_videoID.json --db-path custom.db
    """
    import json
    from pathlib import Path

    downloader = YouTubeChatDownloader(db_path, db_type=db_type)

    try:
        console.print(f"[cyan]Reading JSON file: {json_path}[/cyan]")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        video_info = data.get('video_info')
        chat_messages = data.get('chat_messages', [])
        metadata = data.get('export_metadata', {})

        if not video_info:
            console.print("[red]Error: Invalid JSON format - missing video_info[/red]")
            return

        video_id = video_info.get('video_id')
        console.print(f"[blue]Video ID: {video_id}[/blue]")
        console.print(f"[blue]Title: {video_info.get('title', 'N/A')}[/blue]")
        console.print(f"[cyan]Total messages: {len(chat_messages)}[/cyan]")

        # 检查是否已存在
        from ..database.models import ChatMessage
        with downloader.db_manager.get_session() as session:
            existing = session.query(ChatMessage).filter_by(video_id=video_id).first()
            if existing:
                console.print(f"[yellow]Warning: Video {video_id} already has messages in database[/yellow]")
                if not click.confirm("Continue importing?", default=False):
                    console.print("[yellow]Import cancelled[/yellow]")
                    return

        # 保存到数据库
        console.print("[cyan]Saving video info to database...[/cyan]")
        downloader.save_video_to_db(video_info)

        console.print("[cyan]Saving chat messages to database...[/cyan]")
        downloader.save_chat_messages_to_db(chat_messages)

        console.print(f"[green]✅ Successfully imported {len(chat_messages)} messages for video {video_id}[/green]")

    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON file - {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error importing JSON: {e}[/red]")


if __name__ == '__main__':
    cli()
