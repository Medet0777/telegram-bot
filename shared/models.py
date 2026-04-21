from datetime import datetime
from enum import Enum
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Category(str, Enum):
    PHYSICAL = "physical"
    PSYCHOLOGICAL = "psychological"
    SEXUAL = "sexual"
    DOMESTIC = "domestic"
    OTHER = "other"


CATEGORY_LABELS_KZ = {
    Category.PHYSICAL: "Физикалық зорлық",
    Category.PSYCHOLOGICAL: "Психологиялық зорлық",
    Category.SEXUAL: "Сексуалдық зорлық",
    Category.DOMESTIC: "Отбасылық зорлық",
    Category.OTHER: "Басқа",
}


class Status(str, Enum):
    NEW = "new"
    READ = "read"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


STATUS_LABELS_KZ = {
    Status.NEW: "Жаңа",
    Status.READ: "Оқылды",
    Status.IN_PROGRESS: "Жұмыста",
    Status.CLOSED: "Жабылды",
}


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tg_chat_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    messages: Mapped[list["Message"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(32), default=Category.OTHER.value)
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default=Status.NEW.value, index=True)
    ai_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    session: Mapped["Session"] = relationship(back_populates="messages")
    replies: Mapped[list["AdminReply"]] = relationship(back_populates="message", cascade="all, delete-orphan")


class AdminReply(Base):
    __tablename__ = "admin_replies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    message: Mapped["Message"] = relationship(back_populates="replies")
