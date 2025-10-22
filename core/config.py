"""
Enterprise Configuration Management
Secure, validated configuration with environment isolation
"""

import secrets
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseSettings, Field, validator


class SecurityConfig(BaseSettings):
    """Security-specific configuration"""

    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(64))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MAX_LOGIN_ATTEMPTS: int = 3
    SESSION_TIMEOUT: int = 3600
    PASSWORD_MIN_LENGTH: int = 12
    REQUIRE_MFA: bool = True

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    RATE_LIMIT_PER_HOUR: int = 100
    RATE_LIMIT_PER_DAY: int = 500


class DatabaseConfig(BaseSettings):
    """Database configuration"""

    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/social_lookup"
    REDIS_URL: str = "redis://localhost:6379/0"
    MAX_CONNECTIONS: int = 20
    CONNECTION_TIMEOUT: int = 30

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("Invalid database URL format")
        return v


class AgentConfig(BaseSettings):
    """AI Agents configuration"""

    AGENT_TIMEOUT: int = 300
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5
    CONFIDENCE_THRESHOLD: float = 0.85
    ENABLE_FUZZY_MATCHING: bool = True
    ENABLE_IMAGE_ANALYSIS: bool = True
    ENABLE_FEEDBACK_LOOP: bool = True

    # Platform-specific timeouts
    LINKEDIN_TIMEOUT: int = 30
    GITHUB_TIMEOUT: int = 15
    TWITTER_TIMEOUT: int = 20
    FACEBOOK_TIMEOUT: int = 25
    INSTAGRAM_TIMEOUT: int = 35


class ProxyConfig(BaseSettings):
    """Proxy rotation configuration"""

    PROXY_ENABLED: bool = True
    PROXY_TIMEOUT: int = 10
    MAX_PROXY_RETRIES: int = 3
    PROXY_HEALTH_CHECK_INTERVAL: int = 300

    # Proxy sources (can be files, APIs, or lists)
    PROXY_SOURCES: List[str] = ["proxies/residential.txt", "proxies/datacenter.txt"]


class Settings(BaseSettings):
    """Main application settings"""

    # Core
    APP_NAME: str = "Cyberzilla Social Lookup"
    VERSION: str = "2.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Security
    security: SecurityConfig = SecurityConfig()

    # Database
    database: DatabaseConfig = DatabaseConfig()

    # AI Agents
    agents: AgentConfig = AgentConfig()

    # Proxy
    proxy: ProxyConfig = ProxyConfig()

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/cyberzilla.log"
    ENABLE_AUDIT_LOG: bool = True

    # External APIs (if any)
    EMAIL_VALIDATION_API: Optional[str] = None
    IMAGE_RECOGNITION_API: Optional[str] = None

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False

    @classmethod
    def load_from_yaml(cls, config_path: str = "config.yaml") -> "Settings":
        """Load configuration from YAML file"""
        if Path(config_path).exists():
            with open(config_path, "r") as f:
                yaml_config = yaml.safe_load(f)
            return cls(**yaml_config)
        return cls()


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings.load_from_yaml()
    return _settings


def reload_settings() -> Settings:
    """Reload settings (useful for testing)"""
    global _settings
    _settings = Settings.load_from_yaml()
    return _settings
