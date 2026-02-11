"""
Database Configuration
SQLAlchemy setup and database connection
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from core.config import settings
from core.logging.logger import db_logger


# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db_logger.error(f"Database session error: {str(e)}", method="SESSION")
        raise
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        db_logger.info("Database initialized successfully", method="INIT")
    except Exception as e:
        db_logger.error(f"Database initialization failed: {str(e)}", method="INIT")
        raise


def check_db_connection() -> bool:
    """
    Check if database connection is working
    
    Returns:
        bool: True if connection successful
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        db_logger.error(f"Database connection check failed: {str(e)}", method="CHECK")
        return False
