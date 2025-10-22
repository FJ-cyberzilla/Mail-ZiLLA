"""
BASE AGENT FRAMEWORK - Foundation for all platform agents
Enterprise-grade agent architecture with performance tracking and error handling
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
import random

from .config import get_settings
from .schemas import ProfileData, PlatformType

class AgentStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    OFFLINE = "offline"
    RATE_LIMITED = "rate_limited"

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
    """
    Abstract base class for all platform agents
    Provides common functionality, metrics tracking, and error handling
    """
    
    def __init__(self, platform: PlatformType, agent_name: str = None):
        self.platform = platform
        self.agent_name = agent_name or f"{platform.value}_agent"
        self.logger = logging.getLogger(f"agent.{platform.value}")
        
        # Configuration
        self.settings = get_settings()
        self.timeout = getattr(self.settings.agents, f"{platform.value.upper()}_TIMEOUT", 30)
        self.rate_limit = getattr(self.settings.agents, f"{platform.value.upper()}_RATE_LIMIT", 10)
        self.max_retries = self.settings.agents.MAX_RETRIES
        
        # State
        self.proxy = None
        self.status = AgentStatus.HEALTHY
        self.metrics = AgentMetrics()
        self.rate_limit_reset = None
        self.session = None
        
        # Platform-specific configuration
        self.platform_config = self._load_platform_config()
        
        self.logger.info(f"🤖 Initialized {self.agent_name} for {platform.value}")

    def _load_platform_config(self) -> Dict[str, Any]:
        """Load platform-specific configuration"""
        configs = {
            PlatformType.LINKEDIN: {
                'base_url': 'https://www.linkedin.com',
                'search_endpoint': '/search/results/people/',
                'required_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
            },
            PlatformType.GITHUB: {
                'base_url': 'https://api.github.com',
                'search_endpoint': '/search/users',
                'required_headers': {
                    'User-Agent': 'Cyberzilla-Enterprise/2.1.0',
                    'Accept': 'application/vnd.github.v3+json',
                }
            },
            PlatformType.TWITTER: {
                'base_url': 'https://api.twitter.com',
                'search_endpoint': '/2/users/by',
                'required_headers': {
                    'User-Agent': 'Cyberzilla-Enterprise/2.1.0',
                    'Accept': 'application/json',
                }
            },
            PlatformType.FACEBOOK: {
                'base_url': 'https://graph.facebook.com',
                'search_endpoint': '/v12.0/search',
                'required_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                }
            },
            PlatformType.INSTAGRAM: {
                'base_url': 'https://www.instagram.com',
                'search_endpoint': '/api/v1/users/search/',
                'required_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                }
            }
        }
        return configs.get(self.platform, {})

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers=self.platform_config.get('required_headers', {})
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    @abstractmethod
    async def search_by_email(self, email: str, context: Dict[str, Any] = None) -> List[ProfileData]:
        """
        Search platform by email address
        Must be implemented by each platform agent
        """
        pass

    @abstractmethod
    async def search_by_phone(self, phone: str, context: Dict[str, Any] = None) -> List[ProfileData]:
        """
        Search platform by phone number  
        Must be implemented by each platform agent
        """
        pass

    async def search_with_context(self, identifier: str, strategy: Dict[str, Any], 
                                context: Dict[str, Any], user_context: Dict[str, Any]) -> List[ProfileData]:
        """
        Enhanced search using correlation context
        Can be overridden by platform agents for advanced functionality
        """
        # Default implementation - try both email and phone
        profiles = []
        
        if '@' in identifier:
            profiles = await self.search_by_email(identifier, context)
        elif identifier.startswith('+'):
            profiles = await self.search_by_phone(identifier, context)
        
        return profiles

    async def health_check(self) -> bool:
        """
        Comprehensive agent health check
        """
        try:
            # Check if we're rate limited
            if (self.rate_limit_reset and 
                datetime.now() < self.rate_limit_reset):
                self.status = AgentStatus.RATE_LIMITED
                return False

            # Test basic connectivity to platform
            test_url = f"{self.platform_config.get('base_url', '')}/"
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url, timeout=10) as response:
                    if response.status in [200, 401, 403]:
                        self.status = AgentStatus.HEALTHY
                        return True
                    else:
                        self.status = AgentStatus.DEGRADED
                        return False

        except Exception as e:
            self.logger.warning(f"Health check failed for {self.agent_name}: {e}")
            self.status = AgentStatus.OFFLINE
            return False

    def set_proxy(self, proxy_url: str):
        """Set proxy for agent requests"""
        self.proxy = proxy_url
        self.logger.debug(f"Proxy set for {self.agent_name}: {proxy_url}")

    async def _make_request(self, method: str, url: str, **kwargs) -> Tuple[bool, Any]:
        """
        Make HTTP request with comprehensive error handling and metrics tracking
        """
        start_time = datetime.now()
        self.metrics.total_requests += 1

        try:
            # Rate limiting check
            if self._is_rate_limited():
                self.logger.warning(f"Rate limited for {self.agent_name}")
                return False, "Rate limit exceeded"

            # Prepare request
            request_kwargs = {
                'timeout': self.timeout,
                'headers': self.platform_config.get('required_headers', {})
            }
            
            if self.proxy:
                request_kwargs['proxy'] = self.proxy
            
            request_kwargs.update(kwargs)

            # Make request
            async with self.session.request(method, url, **request_kwargs) as response:
                response_time = (datetime.now() - start_time).total_seconds()
                self.metrics.total_response_time += response_time
                self.metrics.last_request = datetime.now()

                # Handle rate limiting
                if response.status == 429:
                    self._handle_rate_limit(response)
                    return False, "Rate limited by platform"

                # Handle successful response
                if 200 <= response.status < 300:
                    self.metrics.successful_requests += 1
                    self.metrics.last_success = datetime.now()
                    self.metrics.consecutive_failures = 0
                    
                    content = await response.text()
                    return True, content

                # Handle errors
                else:
                    self.metrics.failed_requests += 1
                    self.metrics.consecutive_failures += 1
                    
                    error_msg = f"HTTP {response.status}: {response.reason}"
                    self.logger.warning(f"Request failed for {self.agent_name}: {error_msg}")
                    
                    # Update status based on consecutive failures
                    if self.metrics.consecutive_failures > 3:
                        self.status = AgentStatus.DEGRADED
                    
                    return False, error_msg

        except asyncio.TimeoutError:
            self.metrics.failed_requests += 1
            self.metrics.consecutive_failures += 1
            self.logger.warning(f"Request timeout for {self.agent_name}")
            return False, "Request timeout"

        except Exception as e:
            self.metrics.failed_requests += 1
            self.metrics.consecutive_failures += 1
            self.logger.error(f"Request exception for {self.agent_name}: {e}")
            return False, str(e)

    def _is_rate_limited(self) -> bool:
        """Check if agent is currently rate limited"""
        return (self.rate_limit_reset and 
                datetime.now() < self.rate_limit_reset)

    def _handle_rate_limit(self, response):
        """Handle rate limiting response from platform"""
        self.status = AgentStatus.RATE_LIMITED
        self.metrics.consecutive_failures += 1
        
        # Parse rate limit reset time from headers
        reset_header = response.headers.get('X-RateLimit-Reset')
        if reset_header:
            try:
                reset_time = datetime.fromtimestamp(int(reset_header))
                self.rate_limit_reset = reset_time
            except:
                # Default to 1 hour if can't parse
                self.rate_limit_reset = datetime.now() + timedelta(hours=1)
        else:
            # Default backoff
            self.rate_limit_reset = datetime.now() + timedelta(minutes=5)
        
        self.logger.warning(f"Rate limited until {self.rate_limit_reset}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        total_requests = self.metrics.total_requests or 1  # Avoid division by zero
        
        return {
            'agent_name': self.agent_name,
            'platform': self.platform.value,
            'status': self.status.value,
            'success_rate': self.metrics.successful_requests / total_requests,
            'avg_response_time': self.metrics.total_response_time / total_requests,
            'total_requests': self.metrics.total_requests,
            'failed_requests': self.metrics.failed_requests,
            'consecutive_failures': self.metrics.consecutive_failures,
            'last_request': self.metrics.last_request,
            'last_success': self.metrics.last_success,
            'is_rate_limited': self._is_rate_limited(),
            'rate_limit_reset': self.rate_limit_reset,
        }

    async def enrich_profile_data(self, profile: ProfileData) -> ProfileData:
        """
        Enrich profile data with platform-specific information
        Can be overridden by platform agents
        """
        # Base implementation - platform agents can add more data
        profile.platform = self.platform
        return profile

    def _calculate_confidence_score(self, profile_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score for profile match
        Platform agents can override with custom logic
        """
        confidence_factors = []
        
        # Email match
        if profile_data.get('email_verified'):
            confidence_factors.append(0.9)
        
        # Name consistency
        if profile_data.get('full_name'):
            confidence_factors.append(0.7)
        
        # Profile completeness
        filled_fields = sum(1 for field in [
            profile_data.get('full_name'),
            profile_data.get('location'), 
            profile_data.get('company'),
            profile_data.get('profile_picture')
        ] if field)
        
        completeness_score = filled_fields / 4
        confidence_factors.append(completeness_score * 0.6)
        
        # Activity recency
        if profile_data.get('last_activity'):
            days_ago = (datetime.now() - profile_data['last_activity']).days
            recency_score = max(0, 1 - (days_ago / 365))
            confidence_factors.append(recency_score * 0.5)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.3

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None

class BaseSocialAgent(BaseAgent):
    """
    Base class for social media platforms
    Provides common social media functionality
    """
    
    async def extract_profile_data(self, profile_url: str) -> ProfileData:
        """
        Extract detailed profile data from URL
        Must be implemented by social platform agents
        """
        raise NotImplementedError("extract_profile_data must be implemented by social platform agents")

    async def search_by_username(self, username: str, context: Dict[str, Any] = None) -> List[ProfileData]:
        """
        Search by username - common for social platforms
        """
        # Base implementation - platform agents should override
        return []

    async def validate_profile(self, profile_data: ProfileData) -> bool:
        """
        Validate profile data quality
        """
        return bool(profile_data.full_name or profile_data.username)

class BaseCodeAgent(BaseAgent):
    """
    Base class for code/platform platforms like GitHub, GitLab
    """
    
    async def get_repositories(self, username: str) -> List[Dict[str, Any]]:
        """
        Get user repositories
        """
        return []

    async def analyze_activity(self, username: str) -> Dict[str, Any]:
        """
        Analyze user activity patterns
        """
        return {
            'commit_frequency': 0,
            'recent_activity': False,
            'project_count': 0
        }

    async def get_contribution_graph(self, username: str) -> Dict[str, Any]:
        """
        Get contribution activity graph
        """
        return {}
