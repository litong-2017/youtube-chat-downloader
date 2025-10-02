"""Chat data analysis functionality."""

import pandas as pd
from sqlalchemy import func
from typing import Dict, List, Optional

from ..database.connection import DatabaseManager
from ..database.models import ChatMessage, Video
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ChatAnalyzer:
    """Analyze chat data from the database."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_manager = DatabaseManager(db_path)
    
    def get_chat_by_video(self, video_id: str) -> pd.DataFrame:
        """Get chat messages for a specific video."""
        with self.db_manager.get_session() as session:
            query = session.query(ChatMessage).filter_by(
                video_id=video_id
            ).order_by(ChatMessage.timestamp_usec)
            
            df = pd.read_sql(query.statement, self.db_manager.get_engine())
            return df
    
    def get_top_chatters(self, limit: int = 10) -> pd.DataFrame:
        """Get the most active chatters."""
        with self.db_manager.get_session() as session:
            query = session.query(
                ChatMessage.author_name,
                func.count(ChatMessage.id).label('message_count')
            ).filter(
                ChatMessage.author_name.isnot(None),
                ChatMessage.author_name != ''
            ).group_by(
                ChatMessage.author_name
            ).order_by(
                func.count(ChatMessage.id).desc()
            ).limit(limit)
            
            df = pd.read_sql(query.statement, self.db_manager.get_engine())
            return df
    
    def get_statistics(self) -> Dict:
        """Get general statistics about the data."""
        with self.db_manager.get_session() as session:
            video_count = session.query(func.count(Video.video_id)).scalar()
            message_count = session.query(func.count(ChatMessage.id)).scalar()
            
            # Top videos by message count
            top_videos = session.query(
                ChatMessage.video_id,
                func.count(ChatMessage.id).label('message_count')
            ).group_by(
                ChatMessage.video_id
            ).order_by(
                func.count(ChatMessage.id).desc()
            ).limit(5).all()
            
            return {
                'video_count': video_count,
                'message_count': message_count,
                'top_videos': [(v.video_id, v.message_count) for v in top_videos]
            }
    
    def export_to_csv(
        self, 
        video_id: Optional[str] = None, 
        output_file: str = "chat_export.csv"
    ) -> None:
        """Export chat data to CSV."""
        with self.db_manager.get_session() as session:
            if video_id:
                query = session.query(
                    ChatMessage, Video.title.label('video_title')
                ).join(Video).filter(ChatMessage.video_id == video_id)
            else:
                query = session.query(
                    ChatMessage, Video.title.label('video_title')
                ).join(Video)
            
            df = pd.read_sql(query.statement, self.db_manager.get_engine())
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Data exported to {output_file}")
