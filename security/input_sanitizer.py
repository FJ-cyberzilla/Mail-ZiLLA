"""
INPUT SANITIZER - Security input validation and sanitization
"""

import html
import re


def sanitize_input(input_string: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    """
    if not input_string:
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r"[;\\/*?|&<>$(){}[\]]", "", input_string)

    # HTML escape
    sanitized = html.escape(sanitized)

    # Trim whitespace
    sanitized = sanitized.strip()

    return sanitized


def validate_email_format(email: str) -> bool:
    """
    Basic email format validation
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone_format(phone: str) -> bool:
    """
    Basic international phone format validation
    """
    pattern = r"^\+[1-9]\d{1,14}$"
    return bool(re.match(pattern, phone))
