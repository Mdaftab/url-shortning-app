"""
Utility functions for URL shortening service.
"""
import validators
import secrets
import string
from sqlalchemy.orm import Session
from database import URL


def validate_url(url: str) -> bool:
    """
    Validate if the provided string is a valid URL.
    
    Args:
        url: The URL string to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    if not url:
        return False
    
    # Ensure URL has a protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return validators.url(url)


def normalize_url(url: str) -> str:
    """
    Normalize URL by ensuring it has a protocol.
    
    Args:
        url: The URL string to normalize
        
    Returns:
        Normalized URL with protocol
    """
    if not url.startswith(('http://', 'https://')):
        return 'https://' + url
    return url


def generate_short_code(length: int = 6) -> str:
    """
    Generate a random alphanumeric short code.
    
    Args:
        length: Length of the short code (default: 6)
        
    Returns:
        Random alphanumeric string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def get_unique_short_code(db: Session, length: int = 6, max_attempts: int = 10) -> str:
    """
    Generate a unique short code that doesn't exist in the database.
    
    Args:
        db: Database session
        length: Length of the short code
        max_attempts: Maximum attempts to generate unique code
        
    Returns:
        Unique short code
        
    Raises:
        Exception: If unable to generate unique code after max_attempts
    """
    for _ in range(max_attempts):
        code = generate_short_code(length)
        existing_url = db.query(URL).filter(URL.short_code == code).first()
        if not existing_url:
            return code
    
    # If still not unique, try with longer code
    return generate_short_code(length + 2)

