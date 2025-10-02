"""Database models using SQLAlchemy."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Video(Base):
    """Video model for storing YouTube video information."""

    __tablename__ = "videos"

    video_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(Text)
    upload_date: Mapped[Optional[str]] = mapped_column(String(10), index=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer)
    view_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    channel_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    channel_name: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_live: Mapped[bool] = mapped_column(Boolean, default=False)
    was_live: Mapped[bool] = mapped_column(Boolean, default=False)

    # 直播详细信息
    live_start_timestamp: Mapped[Optional[int]] = mapped_column(BigInteger)  # 直播开始时间戳
    live_end_timestamp: Mapped[Optional[int]] = mapped_column(BigInteger)  # 直播结束时间戳
    release_timestamp: Mapped[Optional[int]] = mapped_column(BigInteger)  # 发布时间戳
    thumbnail: Mapped[Optional[str]] = mapped_column(Text)  # 缩略图URL
    categories: Mapped[Optional[str]] = mapped_column(Text)  # 分类（JSON）
    tags: Mapped[Optional[str]] = mapped_column(Text)  # 标签（JSON）
    like_count: Mapped[Optional[int]] = mapped_column(BigInteger)  # 点赞数
    comment_count: Mapped[Optional[int]] = mapped_column(BigInteger)  # 评论数
    live_status: Mapped[Optional[str]] = mapped_column(String(50))  # 直播状态：is_live, was_live, not_live
    availability: Mapped[Optional[str]] = mapped_column(String(50))  # 可用性状态
    uploader: Mapped[Optional[str]] = mapped_column(String(100))  # 上传者
    uploader_id: Mapped[Optional[str]] = mapped_column(String(100))  # 上传者ID

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class ChatMessage(Base):
    """Chat message model for storing chat data."""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(String(20), index=True)
    message_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    author_name: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    author_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    message: Mapped[Optional[str]] = mapped_column(Text)
    timestamp_usec: Mapped[Optional[int]] = mapped_column(BigInteger, index=True)
    timestamp_text: Mapped[Optional[str]] = mapped_column(String(20))
    message_type: Mapped[str] = mapped_column(String(50), default="text_message", index=True)
    superchat_amount: Mapped[Optional[float]] = mapped_column(Float)
    superchat_currency: Mapped[Optional[str]] = mapped_column(String(10))
    badges: Mapped[Optional[str]] = mapped_column(Text)
    emotes: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of emoji objects
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
