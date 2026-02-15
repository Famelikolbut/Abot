from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Video(Base):
    __tablename__ = 'videos'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = Column(String, nullable=False)
    video_created_at = Column(DateTime(timezone=True), nullable=False)
    views_count = Column(BigInteger, default=0)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    reports_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    snapshots = relationship("VideoSnapshot", back_populates="video", cascade="all, delete-orphan")

class VideoSnapshot(Base):
    __tablename__ = 'video_snapshots'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String, ForeignKey('videos.id'), nullable=False)
    views_count = Column(BigInteger, default=0)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    reports_count = Column(Integer, default=0)
    
    delta_views_count = Column(BigInteger, default=0)
    delta_likes_count = Column(Integer, default=0)
    delta_reports_count = Column(Integer, default=0)
    delta_comments_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    video = relationship("Video", back_populates="snapshots")
