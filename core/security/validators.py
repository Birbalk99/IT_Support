"""
Security Validators
Functions to validate security requirements
"""
import re
from typing import Tuple
from core.config import settings


def is_endpoint_allowed(path: str) -> bool:
    """
    Check if the endpoint path is in the allowed list
    
    Args:
        path: The request path to validate
        
    Returns:
        bool: True if endpoint is allowed, False otherwise
    """
    # Always allow health check
    if path == "/health":
        return True
    
    # Check against allowed endpoints
    for allowed_endpoint in settings.ALLOWED_ENDPOINTS:
        if path.startswith(allowed_endpoint):
            return True
    
    return False


def validate_user_id(user_id: str) -> Tuple[bool, str]:
    """
    Validate user ID format and authenticity
    
    Args:
        user_id: The user ID to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not user_id:
        return False, "User ID is required"
    
    # Check minimum length
    if len(user_id) < 3:
        return False, "User ID is too short"
    
    # Check maximum length
    if len(user_id) > 100:
        return False, "User ID is too long"
    
    # Check for valid characters (alphanumeric, dash, underscore)
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        return False, "User ID contains invalid characters"
    
    # Additional validation can be added here:
    # - Check against database
    # - Validate JWT token
    # - Check user status/permissions
    
    return True, ""


def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Validate API key (for service-to-service communication)
    
    Args:
        api_key: The API key to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not api_key:
        return False, "API key is required"
    
    # Implement API key validation logic
    # This is a placeholder - implement actual validation
    
    return True, ""


def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        input_str: The input string to sanitize
        
    Returns:
        str: Sanitized string
    """
    if not input_str:
        return ""
    
    # Remove potentially dangerous characters
    # This is a basic implementation - enhance based on your needs
    sanitized = re.sub(r'[<>\"\'%;()&+]', '', input_str)
    
    return sanitized.strip()
