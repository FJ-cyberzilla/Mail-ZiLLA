# core/base_agent.py
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class Platform(Enum):
    LINKEDIN = "linkedin"
    GITHUB = "github"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


@dataclass
class ProfileData:
    platform: Platform
    profile_url: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    last_activity: Optional[str] = None
    confidence_score: float = 0.0
    raw_data: Dict[str, Any] = None


class BaseAgent(ABC):
    """Abstract base class for all platform agents"""

    def __init__(self, platform: Platform):
        self.platform = platform
        self.logger = logging.getLogger(f"{platform.value}_agent")

    @abstractmethod
    async def search_by_email(
        self, email: str, context: Dict = None
    ) -> List[ProfileData]:
        """Search platform by email address"""
        pass

    @abstractmethod
    async def search_by_phone(
        self, phone: str, context: Dict = None
    ) -> List[ProfileData]:
        """Search platform by phone number"""
        pass


class BaseSocialAgent(BaseAgent):
    """Base class for social media platforms"""

    pass


class BaseCodeAgent(BaseAgent):
    """Base class for code/platform platforms"""

    pass
