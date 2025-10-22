"""
Enterprise Security Management
Advanced security, authentication, and access control
"""

import hashlib
import hmac
import logging
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import jwt

from .config import get_settings
from .exceptions import SecurityViolation


@dataclass
class UserSession:
    """User session management"""

    username: str
    token: str
    created_at: float
    last_activity: float
    ip_address: str
    user_agent: str


class Authentication:
    """Enterprise authentication system"""

    def __init__(self):
        self.settings = get_settings()
        self.users_db = "data/users.db"
        self._init_users_db()

    def _init_users_db(self):
        """Initialize users database"""
        Path("data").mkdir(exist_ok=True)
        conn = sqlite3.connect(self.users_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                email TEXT,
                role TEXT DEFAULT 'analyst',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN
            )
        """
        )

        # Create default admin user if not exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
        if cursor.fetchone()[0] == 0:
            default_password = self._hash_password("Cyberzilla123!")
            cursor.execute(
                "INSERT INTO users (username, password_hash, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
                (
                    "admin",
                    default_password,
                    "System Administrator",
                    "cyberzilla.systems@gmail.com",
                    "admin",
                ),
            )

        conn.commit()
        conn.close()

    def _hash_password(self, password: str) -> str:
        """Secure password hashing"""
        salt = hashlib.sha256(self.settings.security.SECRET_KEY.encode()).hexdigest()
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return hmac.compare_digest(self._hash_password(plain_password), hashed_password)

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return JWT token"""
        # Check rate limiting
        if self._is_rate_limited(username):
            raise SecurityViolation("Rate limit exceeded for authentication attempts")

        conn = sqlite3.connect(self.users_db)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password_hash, is_active FROM users WHERE username = ?", (username,)
        )
        result = cursor.fetchone()

        if not result or not result[1]:
            self._log_login_attempt(username, "0.0.0.0", False)
            conn.close()
            return None

        stored_hash, is_active = result

        if not is_active or not self.verify_password(password, stored_hash):
            self._log_login_attempt(username, "0.0.0.0", False)
            conn.close()
            return None

        # Update last login and generate token
        cursor.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?",
            (username,),
        )
        self._log_login_attempt(username, "0.0.0.0", True)
        conn.commit()
        conn.close()

        return self._create_access_token(username)

    def _create_access_token(self, username: str) -> str:
        """Create JWT access token"""
        expires_delta = timedelta(
            minutes=self.settings.security.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        expire = datetime.utcnow() + expires_delta

        payload = {
            "sub": username,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access_token",
        }

        return jwt.encode(
            payload,
            self.settings.security.SECRET_KEY,
            algorithm=self.settings.security.ALGORITHM,
        )

    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return username"""
        try:
            payload = jwt.decode(
                token,
                self.settings.security.SECRET_KEY,
                algorithms=[self.settings.security.ALGORITHM],
            )
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except jwt.PyJWTError:
            return None

    def _is_rate_limited(self, username: str) -> bool:
        """Check if user is rate limited"""
        conn = sqlite3.connect(self.users_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM login_attempts 
            WHERE username = ? AND timestamp > datetime('now', '-1 hour')
        """,
            (username,),
        )

        attempts = cursor.fetchone()[0]
        conn.close()

        return attempts >= self.settings.security.MAX_LOGIN_ATTEMPTS

    def _log_login_attempt(self, username: str, ip_address: str, success: bool):
        """Log login attempt for security monitoring"""
        conn = sqlite3.connect(self.users_db)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO login_attempts (username, ip_address, success) VALUES (?, ?, ?)",
            (username, ip_address, success),
        )
        conn.commit()
        conn.close()


class SecurityManager:
    """Comprehensive security management"""

    def __init__(self):
        self.settings = get_settings()
        self.auth = Authentication()
        self.audit_log = "logs/security_audit.log"
        Path("logs").mkdir(exist_ok=True)

    def pre_launch_checks(self) -> bool:
        """Perform security checks before system launch"""
        checks = [
            self._check_secret_key(),
            self._check_database_connection(),
            self._check_file_permissions(),
            self._check_environment(),
        ]

        return all(checks)

    def _check_secret_key(self) -> bool:
        """Verify secret key is properly set"""
        if self.settings.security.SECRET_KEY.startswith("default_"):
            logging.error("Default secret key detected - change immediately!")
            return False
        return True

    def _check_database_connection(self) -> bool:
        """Verify database connectivity"""
        try:
            import sqlite3

            conn = sqlite3.connect(self.auth.users_db)
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Database connection check failed: {e}")
            return False

    def _check_file_permissions(self) -> bool:
        """Check critical file permissions"""
        critical_files = [self.auth.users_db, self.audit_log, ".env"]

        for file_path in critical_files:
            if Path(file_path).exists():
                if Path(file_path).stat().st_mode & 0o777 != 0o600:
                    logging.warning(f"Insecure permissions for {file_path}")

        return True

    def _check_environment(self) -> bool:
        """Check runtime environment security"""
        if self.settings.DEBUG and self.settings.ENVIRONMENT == "production":
            logging.warning("Debug mode enabled in production environment")

        return True

    def validate_email_access(self, username: str, email: str) -> bool:
        """Validate if user has permission to lookup specific email"""
        # Implement domain-based access control
        allowed_domains = self._get_user_allowed_domains(username)
        email_domain = email.split("@")[-1] if "@" in email else ""

        # If no restrictions, allow all
        if not allowed_domains:
            return True

        return email_domain in allowed_domains

    def _get_user_allowed_domains(self, username: str) -> List[str]:
        """Get list of domains user is allowed to query"""
        # This could be loaded from database
        domain_restrictions = {
            "admin": [],  # Empty list means all domains
            "analyst": ["company.com", "partner.org"],
        }

        return domain_restrictions.get(username, [])

    def log_access(self, username: str, action: str, status: str):
        """Log security-relevant actions"""
        timestamp = datetime.now().isoformat()
        log_entry = (
            f"{timestamp} | USER:{username} | ACTION:{action} | STATUS:{status}\n"
        )

        with open(self.audit_log, "a") as f:
            f.write(log_entry)

    def log_operation(self, username: str, operation: str, details: str):
        """Log user operations for audit trail"""
        timestamp = datetime.now().isoformat()
        log_entry = (
            f"{timestamp} | USER:{username} | OP:{operation} | DETAILS:{details}\n"
        )

        with open(self.audit_log, "a") as f:
            f.write(log_entry)


class InputValidator:
    """Input validation and sanitization"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format and common patterns"""
        if not email or "@" not in email:
            return False

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not input_string:
            return ""

        # Remove potentially dangerous characters
        sanitized = re.sub(r"[;\\/*?|&<>$]", "", input_string)
        return sanitized.strip()

    @staticmethod
    def validate_domain(domain: str) -> bool:
        """Validate domain format"""
        pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$"
        return bool(re.match(pattern, domain))
