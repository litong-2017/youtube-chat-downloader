"""Database connection management."""

from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path("data/youtube_chat.db")
        else:
            db_path = Path(db_path)
        
        # Create data directory if it doesn't exist
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables
        self.create_tables()
    
    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def get_engine(self) -> Engine:
        """Get the database engine."""
        return self.engine
