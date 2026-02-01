"""Database connection and session management."""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.auth.models import Base
from app.utils.secrets import get_db_credentials

logger = logging.getLogger(__name__)

_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """Build database URL from credentials."""
    creds = get_db_credentials()
    return (
        f"postgresql://{creds['username']}:{creds['password']}"
        f"@{creds['host']}:{creds['port']}/{creds['dbname']}"
    )


def get_engine():
    """Get or create database engine with connection pooling."""
    global _engine

    if _engine is None:
        database_url = get_database_url()
        _engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
        )
        logger.info("Database engine created")

    return _engine


def get_session_factory():
    """Get or create session factory."""
    global _SessionLocal

    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )

    return _SessionLocal


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Usage:
        with get_db_session() as session:
            user = session.query(User).first()
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_database() -> None:
    """Initialize database tables and create default admin user."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")

    # Create default admin user if not exists
    _create_default_admin()


def _create_default_admin() -> None:
    """Create default admin user if it doesn't exist."""
    import os
    import bcrypt
    from app.auth.models import User

    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")

    if not admin_password:
        logger.warning("ADMIN_PASSWORD not set, skipping default admin creation")
        return

    with get_db_session() as session:
        admin = session.query(User).filter(User.username == admin_username).first()
        if admin is None:
            password_hash = bcrypt.hashpw(
                admin_password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            admin = User(
                username=admin_username,
                email=admin_email,
                password_hash=password_hash,
                is_active=True,
                is_admin=True,
            )
            session.add(admin)
            logger.info(f"Default admin user created (username: {admin_username})")
        else:
            logger.info("Admin user already exists")


def check_database_connection() -> bool:
    """Check if database connection is healthy."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
