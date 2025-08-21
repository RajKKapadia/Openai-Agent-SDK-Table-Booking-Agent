import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class RoleEnum(enum.Enum):
    user = "user"
    assistant = "assistant"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    whatsapp_id = Column(String(56), unique=True, nullable=False)
    channel = Column(String(56), nullable=False, default="whatsapp")

    messages = relationship(
        "Message", back_populates="user", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="messages")
