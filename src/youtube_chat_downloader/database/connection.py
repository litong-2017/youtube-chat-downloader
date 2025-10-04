"""Database connection management."""

from pathlib import Path
from typing import Optional, Literal

from sqlalchemy import create_engine, Engine, Index, event
from sqlalchemy.orm import sessionmaker, Session

from .models import Base, Video, ChatMessage


DbType = Literal["sqlite", "duckdb"]


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(
        self,
        db_path: Optional[str] = None,
        db_type: DbType = "sqlite"
    ):
        """Initialize database manager.

        Args:
            db_path: Path to database file
            db_type: Database type - 'sqlite' or 'duckdb'
        """
        self.db_type = db_type

        # Set default path based on db_type
        if db_path is None:
            if db_type == "sqlite":
                db_path = Path("data/youtube_chat.db")
            else:  # duckdb
                db_path = Path("data/youtube_chat.duckdb")
        else:
            db_path = Path(db_path)

        # Create data directory if it doesn't exist
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path

        # Create engine based on db_type
        if db_type == "sqlite":
            self.engine = create_engine(
                f"sqlite:///{db_path}",
                echo=False
            )
            # Enable foreign keys for SQLite
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()
        elif db_type == "duckdb":
            self.engine = create_engine(
                f"duckdb:///{db_path}",
                echo=False
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables and indexes
        self.create_tables()
        self.create_indexes()

    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(self.engine)

    def create_indexes(self) -> None:
        """Create additional indexes for query optimization."""
        with self.engine.connect() as conn:
            # Video table indexes
            Index('idx_videos_was_live', Video.was_live).create(self.engine, checkfirst=True)
            Index('idx_videos_live_status', Video.live_status).create(self.engine, checkfirst=True)
            Index('idx_videos_live_start', Video.live_start_timestamp).create(self.engine, checkfirst=True)
            Index('idx_videos_view_count', Video.view_count).create(self.engine, checkfirst=True)

            # ChatMessage table composite indexes
            Index('idx_messages_video_timestamp', ChatMessage.video_id, ChatMessage.timestamp_usec).create(self.engine, checkfirst=True)
            Index('idx_messages_author_video', ChatMessage.author_id, ChatMessage.video_id).create(self.engine, checkfirst=True)
            Index('idx_messages_type_video', ChatMessage.message_type, ChatMessage.video_id).create(self.engine, checkfirst=True)

    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()

    def get_engine(self) -> Engine:
        """Get the database engine."""
        return self.engine
