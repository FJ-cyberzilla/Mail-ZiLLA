# core/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import aiohttp
import logging

class Platform(Enum):
    LINKEDIN = "linkedin"
    GITHUB = "github"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"

class AgentStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    OFFLINE = "offline"
    RATE_LIMITED = "rate_limited"

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

@dataclass
class AgentMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    last_request: Optional[datetime] = None
    last_success: Optional[datetime] = None
    consecutive_failures: int = 0

class BaseAgent(ABC):
    """Abstract base class for all platform agents"""
    
    def __init__(self, platform: Platform):
        self.platform = platform
        self.agent_name = f"{platform.value}_agent"
        self.logger = logging.getLogger(f"agent.{platform.value}")
        
        # Configuration
        self.timeout = 30
        self.rate_limit = 10
        self.max_retries = 3
        
        # State
        self.proxy = None
        self.status = AgentStatus.HEALTHY
        self.metrics = AgentMetrics()
        self.rate_limit_reset = None
        self.session = None
        
        self.logger.info(f"Initialized {self.agent_name} for {platform.value}")

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    @abstractmethod
    async def search_by_email(self, email: str, context: Dict = None) -> List[ProfileData]:
        """Search platform by email address"""
        pass
    
    @abstractmethod  
    async def search_by_phone(self, phone: str, context: Dict = None) -> List[ProfileData]:
        """Search platform by phone number"""
        pass
    
    async def health_check(self) -> bool:
        """Check if agent is healthy and operational"""
        try:
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def set_proxy(self, proxy_url: str):
        """Set proxy for agent requests"""
        self.proxy = proxy_url
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            'platform': self.platform.value,
            'last_activity': datetime.now(),
            'is_healthy': True
        }

class BaseSocialAgent(BaseAgent):
    """Base class for social media platforms"""
    
    async def extract_profile_data(self, profile_url: str) -> ProfileData:
        """Extract detailed profile data from URL"""
        pass
    
    async def validate_profile(self, profile_data: ProfileData) -> bool:
        """Validate profile data quality"""
        return True

class BaseCodeAgent(BaseAgent):
    """Base class for code/platform platforms"""
    
    async def get_repositories(self, username: str) -> List[Dict]:
        """Get user repositories"""
        return []
    
    async def analyze_activity(self, username: str) -> Dict[str, Any]:
        """Analyze user activity patterns"""
        return {}
