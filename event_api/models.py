import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, DateTime, Integer, Text, Boolean, Enum, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# ---------- Enums ----------
class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    HEAD = "head"
    EMPLOYEE = "employee"
    STUDENT = "student"

class ConfirmationStatusEnum(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    PENDING = "pending"

class NotificationTypeEnum(str, enum.Enum):
    EVENT = "event"
    OPPORTUNITY = "opportunity"
    SYSTEM = "system"

# ---------- User ----------
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(150), nullable=False, unique=True, index=True)
    email = Column(String(320), nullable=False, unique=True, index=True)
    full_name = Column(String(200), nullable=True)
    hashed_password = Column(String(1024), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.STUDENT)
    department = Column(String(200), nullable=True)  # useful for Head/Employee grouping
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    created_events = relationship("Event", back_populates="creator", cascade="none")
    confirmations = relationship("EventConfirmation", back_populates="student", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete-orphan")

# ---------- Event ----------
class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        # Prevent duplicate events with same title/time in same department (example)
        UniqueConstraint("title", "start_time", name="uq_event_title_start"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    department = Column(String(200), nullable=True)  # optional
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    capacity = Column(Integer, nullable=True)  # optional event capacity
    is_public = Column(Boolean, default=True, nullable=False)

    # Creator tracking (required)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    creator_role = Column(Enum(RoleEnum), nullable=False)

    # Confirmation count MUST be present (application updates this)
    confirmation_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User", back_populates="created_events")
    confirmations = relationship("EventConfirmation", back_populates="event", cascade="all, delete-orphan")

# ---------- Opportunity ----------
class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    link = Column(String(1024), nullable=True)
    department = Column(String(200), nullable=True)
    posted_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    posted_by_role = Column(Enum(RoleEnum), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # relationship if you want poster info
    posted_by = relationship("User", foreign_keys=[posted_by_id])

# ---------- EventConfirmation ----------
class EventConfirmation(Base):
    __tablename__ = "event_confirmations"
    __table_args__ = (
        UniqueConstraint("event_id", "student_id", name="uq_event_student"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    status = Column(Enum(ConfirmationStatusEnum), nullable=False, default=ConfirmationStatusEnum.CONFIRMED)
    note = Column(Text, nullable=True)  # any student note
    confirmed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    event = relationship("Event", back_populates="confirmations")
    student = relationship("User", back_populates="confirmations")

# ---------- Notification ----------
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    type = Column(Enum(NotificationTypeEnum), nullable=False, default=NotificationTypeEnum.SYSTEM)
    related_event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    related_opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    recipient = relationship("User", back_populates="notifications")
    # optional: relations to event/opportunity if you need backrefs (left out to keep simple)
