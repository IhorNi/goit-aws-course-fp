"""Authentication handler with bcrypt password hashing."""

import logging
from datetime import datetime
from typing import Optional, Tuple

import bcrypt

from app.auth.database import get_db_session
from app.auth.models import User

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password.

    Returns:
        Hashed password string.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Plain text password to verify.
        password_hash: Stored password hash.

    Returns:
        True if password matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"), password_hash.encode("utf-8")
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[str]]:
    """
    Authenticate a user for Gradio.

    This function is designed to work with Gradio's auth parameter.

    Args:
        username: Username to authenticate.
        password: Password to verify.

    Returns:
        Tuple of (success, error_message).
        For Gradio compatibility, returns True/False for success.
    """
    if not username or not password:
        return False, "Username and password are required"

    try:
        with get_db_session() as session:
            user = (
                session.query(User)
                .filter(User.username == username)
                .first()
            )

            if user is None:
                logger.warning(f"Authentication failed: user '{username}' not found")
                return False, "Invalid username or password"

            if not user.is_active:
                logger.warning(f"Authentication failed: user '{username}' is inactive")
                return False, "Account is deactivated"

            if not verify_password(password, user.password_hash):
                logger.warning(f"Authentication failed: invalid password for '{username}'")
                return False, "Invalid username or password"

            # Update last login
            user.last_login = datetime.utcnow()
            session.commit()

            logger.info(f"User '{username}' authenticated successfully")
            return True, None

    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return False, "Authentication service unavailable"


def gradio_auth(username: str, password: str) -> bool:
    """
    Gradio-compatible authentication function.

    Args:
        username: Username to authenticate.
        password: Password to verify.

    Returns:
        True if authentication successful, False otherwise.
    """
    success, _ = authenticate_user(username, password)
    return success


def create_user(
    username: str,
    password: str,
    email: Optional[str] = None,
    is_admin: bool = False,
) -> Tuple[Optional[User], Optional[str]]:
    """
    Create a new user.

    Args:
        username: Unique username.
        password: Plain text password (will be hashed).
        email: Optional email address.
        is_admin: Whether user has admin privileges.

    Returns:
        Tuple of (user, error_message).
    """
    if not username or not password:
        return None, "Username and password are required"

    if len(password) < 8:
        return None, "Password must be at least 8 characters"

    try:
        with get_db_session() as session:
            # Check if username exists
            existing = (
                session.query(User)
                .filter(User.username == username)
                .first()
            )
            if existing:
                return None, "Username already exists"

            # Check if email exists
            if email:
                existing_email = (
                    session.query(User)
                    .filter(User.email == email)
                    .first()
                )
                if existing_email:
                    return None, "Email already exists"

            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                is_admin=is_admin,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            logger.info(f"User '{username}' created successfully")
            return user, None

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None, "Failed to create user"


def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username."""
    with get_db_session() as session:
        return session.query(User).filter(User.username == username).first()
