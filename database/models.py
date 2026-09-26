from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    BigInteger, Integer, String, Text, Boolean, Float, Date, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user_id
    full_name: Mapped[str] = mapped_column(String(100))
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="uz")
    source: Mapped[str] = mapped_column(String(100), default="direct")
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_active: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    total_leads: Mapped[int] = mapped_column(Integer, default=0)

    leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="user")


class Manager(Base):
    __tablename__ = "managers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user_id
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(30), default="manager")  # super_admin, manager, content
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    assigned_leads: Mapped[List["Lead"]] = relationship("Lead", back_populates="manager")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lead_number: Mapped[str] = mapped_column(String(30), unique=True, index=True)  # ET-1001
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    service: Mapped[str] = mapped_column(String(50))  # visa, study, tour, consult
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    purpose: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    timeframe: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    refusal_count: Mapped[int] = mapped_column(Integer, default=0)
    stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ielts_score: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    budget: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Client submitted contact details
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    convenient_time: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    source: Mapped[str] = mapped_column(String(100), default="direct")
    status: Mapped[str] = mapped_column(String(50), default="YANGI")
    assigned_to: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("managers.id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    user: Mapped["User"] = relationship("User", back_populates="leads")
    manager: Mapped[Optional["Manager"]] = relationship("Manager", back_populates="assigned_leads")
    history: Mapped[List["StatusHistory"]] = relationship("StatusHistory", back_populates="lead", cascade="all, delete-orphan")
    reminders: Mapped[List["Reminder"]] = relationship("Reminder", back_populates="lead", cascade="all, delete-orphan")


class StatusHistory(Base):
    __tablename__ = "status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(Integer, ForeignKey("leads.id"))
    old_status: Mapped[str] = mapped_column(String(50))
    new_status: Mapped[str] = mapped_column(String(50))
    changed_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="history")


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(Integer, ForeignKey("leads.id"))
    manager_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    remind_at: Mapped[datetime] = mapped_column(DateTime)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="reminders")


class Tour(Base):
    __tablename__ = "tours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    destination: Mapped[str] = mapped_column(String(100))  # Turkiya, Misr, Dubai, etc.
    title: Mapped[str] = mapped_column(String(150))
    price_usd: Mapped[float] = mapped_column(Float)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    description: Mapped[str] = mapped_column(Text)
    whats_included: Mapped[str] = mapped_column(Text)
    slots_total: Mapped[int] = mapped_column(Integer, default=20)
    slots_left: Mapped[int] = mapped_column(Integer, default=20)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class FAQ(Base):
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country: Mapped[str] = mapped_column(String(100))
    topic: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Result(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))
    service: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    photo_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
