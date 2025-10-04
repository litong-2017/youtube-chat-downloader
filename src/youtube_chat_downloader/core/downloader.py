"""Core downloader functionality."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yt_dlp
from chat_downloader import ChatDownloader
from rich.console import Console
from rich.progress import Progress, TaskID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database.connection import DatabaseManager
from ..database.models import ChatMessage, Video
from ..utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


class YouTubeChatDownloader:
    """Main class for downloading YouTube chat data."""

    def __init__(
        self,
        db_path: Optional[str] = None,
        json_output_dir: Optional[str] = None,
        db_type: str = "sqlite",
        cookies_file: Optional[str] = None
    ):
        self.db_manager = DatabaseManager(db_path, db_type=db_type)
        # Initialize ChatDownloader with cookies if provided
        self.chat_downloader = ChatDownloader(cookies=cookies_file if cookies_file else None)
        self.cookies_file = cookies_file

        # 设置JSON输出目录
        if json_output_dir is None:
            self.json_output_dir = Path("data/json_exports")
        else:
            self.json_output_dir = Path(json_output_dir)

        # 创建JSON输出目录
        self.json_output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Get basic channel information."""
        logger.debug(f"Getting channel info for: {channel_id}")

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'ignoreerrors': True,
        }

        # Add cookies if provided
        if self.cookies_file:
            ydl_opts['cookiefile'] = self.cookies_file
        
        # 清理频道ID
        clean_channel_id = channel_id.strip('@')
        
        urls_to_try = [
            f"https://www.youtube.com/@{clean_channel_id}",
            f"https://www.youtube.com/c/{clean_channel_id}",
            f"https://www.youtube.com/user/{clean_channel_id}",
        ]
        
        # 如果看起来像频道ID (UC开头)，直接尝试
        if clean_channel_id.startswith('UC'):
            urls_to_try.insert(0, f"https://www.youtube.com/channel/{clean_channel_id}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in urls_to_try:
                try:
                    logger.debug(f"Getting channel info from: {url}")
                    info = ydl.extract_info(url, download=False)
                    if info:
                        return {
                            'channel_id': info.get('channel_id', ''),
                            'channel_name': info.get('channel', '') or info.get('uploader', ''),
                            'channel_url': info.get('channel_url', ''),
                            'subscriber_count': info.get('subscriber_count'),
                        }
                except Exception as e:
                    logger.debug(f"Failed to get channel info from {url}: {str(e)}")
                    continue
        
        logger.warning(f"Could not get channel info for: {channel_id}")
        return None
    
    def _search_channel_livestreams(self, channel_id: str) -> List[Dict]:
        """Use search to find livestreams from a channel."""
        logger.debug(f"Searching for livestreams from channel: {channel_id}")

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'ignoreerrors': True,
        }

        # Add cookies if provided
        if self.cookies_file:
            ydl_opts['cookiefile'] = self.cookies_file
        
        # 多种搜索策略
        search_queries = [
            f"ytsearch30:{channel_id} 直播",
            f"ytsearch30:{channel_id} live stream",
            f"ytsearch30:{channel_id} 실시간",  # 韩文直播
            f"ytsearch20:site:youtube.com {channel_id} live",
        ]
        
        videos = []
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for query in search_queries:
                try:
                    logger.debug(f"Searching: {query}")
                    info = ydl.extract_info(query, download=False)
                    
                    if info and 'entries' in info:
                        for entry in info['entries']:
                            if not entry or not entry.get('id'):
                                continue
                            
                            title = entry.get('title', '').lower()
                            
                            # 检查标题是否包含直播相关关键词
                            live_keywords = ['直播', 'live', 'stream', '실시간', 'ライブ']
                            if any(keyword in title for keyword in live_keywords):
                                video_info = {
                                    'video_id': entry.get('id'),
                                    'title': entry.get('title', ''),
                                    'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                                    'channel_id': entry.get('channel_id'),
                                    'channel': entry.get('channel'),
                                    'duration': entry.get('duration'),
                                    'was_live': True,  # 从搜索推断
                                }
                                videos.append(video_info)
                
                except Exception as e:
                    logger.debug(f"Search failed for '{query}': {str(e)}")
                    continue
        
        # 去重
        seen_ids = set()
        unique_videos = []
        for video in videos:
            if video['video_id'] not in seen_ids:
                seen_ids.add(video['video_id'])
                unique_videos.append(video)
        
        logger.debug(f"Found {len(unique_videos)} unique videos through search")
        return unique_videos
    
    def get_channel_livestreams(self, channel_id: str) -> List[Dict]:
        """Get all livestream videos from a channel."""
        logger.info(f"Getting livestream videos for channel: {channel_id}")

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'ignoreerrors': True,
            'playlistend': 100000,  # 限制获取数量
        }

        # Add cookies if provided
        if self.cookies_file:
            ydl_opts['cookiefile'] = self.cookies_file
        
        videos = []
        
        # 清理频道ID，移除多余的@符号
        clean_channel_id = channel_id.strip('@')
        
        # 构建多种可能的URL格式
        urls_to_try = []
        
        # 首先尝试获取频道信息
        channel_info = self._get_channel_info(clean_channel_id)
        if channel_info and channel_info.get('channel_id'):
            real_channel_id = channel_info['channel_id']
            logger.debug(f"Found real channel ID: {real_channel_id}")
            urls_to_try.extend([
                f"https://www.youtube.com/channel/{real_channel_id}/streams",
                f"https://www.youtube.com/channel/{real_channel_id}/videos",
            ])
        
        # 标准URL格式
        if clean_channel_id.startswith('UC'):
            urls_to_try.extend([
                f"https://www.youtube.com/channel/{clean_channel_id}/streams",
                f"https://www.youtube.com/channel/{clean_channel_id}/videos",
            ])
        else:
            urls_to_try.extend([
                f"https://www.youtube.com/@{clean_channel_id}/streams",
                f"https://www.youtube.com/@{clean_channel_id}/videos",
                f"https://www.youtube.com/c/{clean_channel_id}/streams",
                f"https://www.youtube.com/c/{clean_channel_id}/videos",
                f"https://www.youtube.com/user/{clean_channel_id}/streams",
                f"https://www.youtube.com/user/{clean_channel_id}/videos",
            ])
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in urls_to_try:
                try:
                    logger.debug(f"Trying URL: {url}")
                    info = ydl.extract_info(url, download=False)
                    
                    if info and 'entries' in info and info['entries']:
                        for entry in info['entries']:
                            if not entry or not entry.get('id'):
                                continue
                            
                            video_info = {
                                'video_id': entry.get('id'),
                                'title': entry.get('title', ''),
                                'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                                'duration': entry.get('duration'),
                                'was_live': entry.get('was_live', False),
                                'is_live': entry.get('is_live', False),
                                'channel_id': entry.get('channel_id'),
                                'channel': entry.get('channel'),
                            }
                            
                            # 如果是从/streams获取的，或者标记为直播，就添加
                            if ('/streams' in url or 
                                video_info['was_live'] or 
                                video_info['is_live'] or
                                any(keyword in video_info['title'].lower() 
                                    for keyword in ['直播', 'live', 'stream'])):
                                videos.append(video_info)
                        
                        if videos:
                            logger.info(f"Successfully found {len(videos)} videos from: {url}")
                            break
                            
                except Exception as e:
                    logger.debug(f"Failed to get videos from {url}: {str(e)}")
                    continue
        
        # 如果还没找到视频，尝试搜索该频道的直播
        if not videos:
            logger.info("No videos found from channel tabs, trying search method...")
            videos = self._search_channel_livestreams(clean_channel_id)
        
        logger.info(f"Found {len(videos)} potential livestream videos")
        return videos
    
    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Get detailed information about a video."""
        logger.debug(f"Getting video info for: {video_id}")

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }

        # Add cookies if provided
        if self.cookies_file:
            ydl_opts['cookiefile'] = self.cookies_file
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={video_id}", 
                    download=False
                )
                if info:
                    import json

                    # 获取最佳缩略图
                    thumbnail = ''
                    if info.get('thumbnails'):
                        thumbnail = info['thumbnails'][-1].get('url', '')
                    elif info.get('thumbnail'):
                        thumbnail = info.get('thumbnail', '')

                    return {
                        'video_id': video_id,
                        'title': info.get('title', ''),
                        'upload_date': info.get('upload_date', ''),
                        'duration': info.get('duration', 0),
                        'view_count': info.get('view_count', 0),
                        'channel_id': info.get('channel_id', ''),
                        'channel_name': info.get('channel', ''),
                        'description': info.get('description', ''),
                        'is_live': info.get('is_live', False),
                        'was_live': info.get('was_live', False) or info.get('live_status') == 'was_live',

                        # 直播详细信息
                        'live_start_timestamp': info.get('release_timestamp') or info.get('timestamp'),
                        'live_end_timestamp': None,  # YouTube API 不直接提供结束时间
                        'release_timestamp': info.get('release_timestamp') or info.get('timestamp'),
                        'thumbnail': thumbnail,
                        'categories': json.dumps(info.get('categories', [])) if info.get('categories') else None,
                        'tags': json.dumps(info.get('tags', [])) if info.get('tags') else None,
                        'like_count': info.get('like_count'),
                        'comment_count': info.get('comment_count'),
                        'live_status': info.get('live_status'),
                        'availability': info.get('availability'),
                        'uploader': info.get('uploader'),
                        'uploader_id': info.get('uploader_id'),
                    }
        except Exception as e:
            logger.error(f"Failed to get video info for {video_id}: {e}")
            return None
    
    def download_chat_for_video(self, video_id: str) -> List[Dict]:
        """Download chat data for a single video."""
        logger.info(f"Downloading chat for video: {video_id}")

        chat_messages = []
        url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            # Get chat (cookies already configured in ChatDownloader instance)
            chat = self.chat_downloader.get_chat(url)
            
            message_count = 0
            for message in chat:
                try:
                    chat_data = {
                        'video_id': video_id,
                        'message_id': message.get('message_id', f"{video_id}_{message_count}"),
                        'author_name': message.get('author', {}).get('name', '') if message.get('author') else '',
                        'author_id': message.get('author', {}).get('id', '') if message.get('author') else '',
                        'message': message.get('message', ''),
                        'timestamp_usec': message.get('timestamp', 0),
                        'timestamp_text': message.get('time_text', ''),
                        'message_type': message.get('message_type', 'text_message'),
                        'superchat_amount': (
                            message.get('money', {}).get('amount', 0)
                            if message.get('money') else None
                        ),
                        'superchat_currency': (
                            message.get('money', {}).get('currency', '')
                            if message.get('money') else None
                        ),
                        'badges': (
                            json.dumps(message.get('author', {}).get('badges', []))
                            if message.get('author', {}).get('badges') else None
                        ),
                        'emotes': (
                            json.dumps(message.get('emotes', []))
                            if message.get('emotes') else None
                        )
                    }
                    
                    chat_messages.append(chat_data)
                    message_count += 1

                except Exception as e:
                    logger.warning(f"Failed to process message: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Failed to download chat for {video_id}: {e}")
            return []
        
        logger.info(f"Downloaded {len(chat_messages)} messages")
        return chat_messages

    def save_chat_to_json(self, video_id: str, video_info: Dict, chat_messages: List[Dict]) -> Optional[str]:
        """Save chat messages to JSON file with date-based naming.

        Args:
            video_id: YouTube video ID
            video_info: Video metadata dictionary
            chat_messages: List of chat message dictionaries

        Returns:
            Path to saved JSON file, or None if failed
        """
        try:
            # 从video_info获取直播日期
            upload_date = video_info.get('upload_date', '')
            if upload_date and len(upload_date) >= 8:
                # upload_date格式: YYYYMMDD
                date_str = upload_date  # 20251001
            else:
                # 如果没有日期，使用当前日期
                date_str = datetime.now().strftime('%Y%m%d')

            # 构建文件名: 日期_视频ID.json
            filename = f"{date_str}_{video_id}.json"
            filepath = self.json_output_dir / filename

            # 构建完整的导出数据结构
            export_data = {
                'video_info': video_info,
                'chat_messages': chat_messages,
                'export_metadata': {
                    'total_messages': len(chat_messages),
                    'exported_at': datetime.now().isoformat(),
                    'video_id': video_id,
                }
            }

            # 写入JSON文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved chat to JSON: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to save chat to JSON: {e}")
            return None

    def save_video_to_db(self, video_info: Dict) -> None:
        """Save video information to database."""
        try:
            with self.db_manager.get_session() as session:
                video = Video(**video_info)
                session.merge(video)  # Use merge to handle duplicates
                session.commit()
                logger.debug(f"Saved video info for: {video_info.get('video_id')}")
        except Exception as e:
            logger.error(f"Failed to save video to database: {e}")
    
    def save_chat_messages_to_db(self, messages: List[Dict]) -> None:
        """Save chat messages to database."""
        if not messages:
            return
        
        try:
            with self.db_manager.get_session() as session:
                saved_count = 0
                for message_data in messages:
                    try:
                        message = ChatMessage(**message_data)
                        session.add(message)
                        saved_count += 1
                    except IntegrityError:
                        session.rollback()
                        logger.debug(f"Duplicate message skipped: {message_data.get('message_id')}")
                        continue
                    except Exception as e:
                        session.rollback()
                        logger.warning(f"Failed to add message: {e}")
                        continue
                
                session.commit()
                logger.info(f"Saved {saved_count} messages to database")
        except Exception as e:
            logger.error(f"Failed to save messages to database: {e}")
    
    def _filter_videos_by_date(
        self,
        videos: List[Dict],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """Filter videos by upload date range."""
        if not start_date and not end_date:
            return videos

        filtered = []
        start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        for video in videos:
            upload_date_str = video.get('upload_date')
            if not upload_date_str:
                # 如果没有日期信息，尝试获取详细信息
                video_info = self.get_video_info(video['video_id'])
                if video_info:
                    upload_date_str = video_info.get('upload_date')

            if upload_date_str:
                try:
                    # upload_date format: YYYYMMDD
                    video_date = datetime.strptime(upload_date_str, '%Y%m%d')

                    if start_dt and video_date < start_dt:
                        continue
                    if end_dt and video_date > end_dt:
                        continue

                    filtered.append(video)
                except ValueError:
                    logger.warning(f"Invalid date format for video {video['video_id']}: {upload_date_str}")
                    filtered.append(video)  # 包含无法解析日期的视频
            else:
                filtered.append(video)  # 包含没有日期的视频

        return filtered

    def _filter_videos_by_index(
        self,
        videos: List[Dict],
        start_index: int = 0,
        end_index: Optional[int] = None
    ) -> List[Dict]:
        """Filter videos by index range."""
        if end_index is None:
            return videos[start_index:]
        return videos[start_index:end_index]

    def download_channel_chat_history(
        self,
        channel_id: str,
        max_videos: Optional[int] = None,
        skip_existing: bool = True,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        start_index: int = 0,
        end_index: Optional[int] = None,
        stop_on_existing: bool = True,
        save_to_db: bool = False
    ) -> None:
        """Download chat history for an entire channel.

        Args:
            channel_id: YouTube channel ID or handle
            max_videos: Maximum number of videos to process
            skip_existing: Skip videos that already have messages in database (incremental mode)
            start_date: Filter videos from this date (YYYY-MM-DD)
            end_date: Filter videos until this date (YYYY-MM-DD)
            start_index: Start processing from this index in video list
            end_index: Stop processing at this index in video list
            stop_on_existing: Stop downloading when encountering first already-downloaded video (default: True)
            save_to_db: Whether to save data to database (default: False, only save to JSON)
        """
        console.print(f"[bold green]Starting download for channel: {channel_id}[/bold green]")

        # 获取所有直播视频
        videos = self.get_channel_livestreams(channel_id)

        if not videos:
            console.print("[bold red]No videos found![/bold red]")
            console.print("[yellow]Suggestions:[/yellow]")
            console.print("1. Check if the channel ID is correct")
            console.print("2. Make sure the channel has livestream videos")
            console.print("3. Try using search mode: --search-mode")
            return

        console.print(f"[cyan]Found {len(videos)} total videos[/cyan]")

        # 应用日期范围过滤
        if start_date or end_date:
            videos = self._filter_videos_by_date(videos, start_date, end_date)
            console.print(f"[cyan]After date filter: {len(videos)} videos[/cyan]")

        # 应用索引范围过滤
        if start_index > 0 or end_index is not None:
            videos = self._filter_videos_by_index(videos, start_index, end_index)
            console.print(f"[cyan]After index filter: {len(videos)} videos[/cyan]")

        # 应用最大数量限制
        if max_videos:
            videos = videos[:max_videos]
            console.print(f"[cyan]Limited to {len(videos)} videos[/cyan]")

        if not videos:
            console.print("[yellow]No videos to process after filtering[/yellow]")
            return

        console.print(f"[bold cyan]Processing {len(videos)} videos...[/bold cyan]\n")

        with Progress() as progress:
            task = progress.add_task(
                "[cyan]Processing videos...",
                total=len(videos)
            )

            successful = 0
            failed = 0
            skipped = 0

            for video in videos:
                video_id = video['video_id']
                video_title = video.get('title', 'Unknown')[:50]

                progress.update(task, description=f"[cyan]Processing {video_id}...")

                try:
                    # 检查是否已下载（增量模式）
                    if skip_existing or stop_on_existing:
                        with self.db_manager.get_session() as session:
                            existing = session.query(ChatMessage).filter_by(
                                video_id=video_id
                            ).first()
                            if existing:
                                if stop_on_existing:
                                    console.print(f"[yellow]🛑 Found already-downloaded video {video_id}, stopping...[/yellow]")
                                    skipped += 1
                                    progress.advance(task)
                                    break  # 停止处理后续视频
                                else:
                                    console.print(f"[yellow]⏭️ Skipping {video_id} (already processed)[/yellow]")
                                    skipped += 1
                                    progress.advance(task)
                                    continue

                    # 获取视频信息
                    video_info = self.get_video_info(video_id)
                    if not video_info:
                        console.print(f"[red]❌ Failed to get video info for {video_id}[/red]")
                        failed += 1
                        progress.advance(task)
                        continue

                    console.print(f"[blue]📺 {video_title}[/blue]")

                    # 下载聊天记录
                    chat_messages = self.download_chat_for_video(video_id)
                    if not chat_messages:
                        console.print(f"[yellow]⚠️ No chat messages found for {video_id}[/yellow]")
                        failed += 1
                        progress.advance(task)
                        continue

                    # 1. 先保存为JSON文件
                    json_path = self.save_chat_to_json(video_id, video_info, chat_messages)
                    if json_path:
                        console.print(f"[cyan]💾 Saved to JSON: {Path(json_path).name}[/cyan]")

                    # 2. 如果启用了save_to_db，保存到数据库
                    if save_to_db:
                        self.save_video_to_db(video_info)
                        self.save_chat_messages_to_db(chat_messages)
                        console.print(f"[green]💬 Saved {len(chat_messages)} messages to database[/green]")

                    successful += 1

                    # 速率限制
                    time.sleep(2)

                except Exception as e:
                    logger.error(f"Error processing {video_id}: {e}")
                    console.print(f"[red]❌ Failed: {video_id} - {str(e)}[/red]")
                    failed += 1

                progress.advance(task)

        console.print(f"\n[bold green]Download complete![/bold green]")
        console.print(f"✅ Successful: {successful}")
        console.print(f"❌ Failed: {failed}")
        console.print(f"⏭️ Skipped: {skipped}")
        console.print(f"[cyan]Total processed: {successful + failed + skipped}/{len(videos)}[/cyan]")
