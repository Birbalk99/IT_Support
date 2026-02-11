"""
Database Models
Define your database models here
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from services.db_services.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = relationship("Ticket", back_populates="creator")


class Ticket(Base):
    """Ticket model"""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50))  # Authentication, Network, Software, Hardware, General
    priority = Column(String(20))  # Low, Medium, High, Critical
    status = Column(String(20), default="Open")  # Open, In Progress, Resolved, Closed
    
    # AI Analysis Fields
    ai_category = Column(String(50))
    ai_priority = Column(String(20))
    suggested_solution = Column(Text)
    estimated_resolution_time = Column(String(50))
    sentiment_score = Column(String(20))
    
    # Assignment
    assigned_to = Column(String(100))
    assigned_team = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Foreign Keys
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", back_populates="tickets")


class SecurityAudit(Base):
    """Security audit log model"""
    __tablename__ = "security_audits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True)
    event_type = Column(String(50), nullable=False)  # Login, Logout, Access, Failed Login
    ip_address = Column(String(50))
    endpoint = Column(String(200))
    method = Column(String(10))
    status_code = Column(Integer)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# Add more models as needed for your application
