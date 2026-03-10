from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String

from models.base import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String(128), nullable=False)
    platform = Column(String(20), nullable=False)
    refresh_token_hash = Column(String(255), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_user_sessions_user_id", "user_id"),
        Index("ix_user_sessions_device_id", "device_id"),
        Index("ix_user_sessions_expires_at", "expires_at"),
        Index("ix_user_sessions_user_device", "user_id", "device_id"),
    )
