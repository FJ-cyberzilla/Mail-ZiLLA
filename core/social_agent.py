"""
SOCIAL AGENT CORE - Enterprise Intelligence Engine v2.0
Expanded Platform Coverage: 15+ Social Networks & Messaging Apps
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .activity_scorer import ActivityScorer
from .config import get_settings
from .exceptions import (ProxyError, RateLimitExceeded, SecurityViolation,
                         ValidationError)
from .feedback_engine import FeedbackEngine
from .fuzzy_matcher import FuzzyMatcher
from .image_analyzer import ImageAnalyzer
from .proxy_manager import ProxyManager
from .strategy_router import StrategyRouter
from .validation import EmailValidator


class SearchStatus(Enum):
    """Search status enumeration"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class PlatformCategory(Enum):
    PROFESSIONAL = "professional"
    SOCIAL_MEDIA = "social_media"
    MESSAGING = "messaging"
    CODE = "code"
    EMERGING = "emerging"
    SPECIALIZED = "specialized"

@dataclass
class ProfileData:
    """Enhanced profile data structure for all platforms"""
    platform: str
    platform_category: PlatformCategory
    profile_url: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None  # For messaging apps
    location: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    profile_picture: Optional[str] = None
    last_activity: Optional[datetime] = None
    bio: Optional[str] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    posts_count: Optional[int] = None
    is_verified: bool = False
    privacy_level: str = "public"  # public, private, restricted
    confidence: float = 0.0
    raw_data: Optional[Dict[str, Any]] = None
    account_age: Optional[timedelta] = None
    language: Optional[str] = None

    def __post_init__(self):
        """Initialize default values"""
        if self.raw_data is None:
            self.raw_data = {}

@dataclass
class CorrelationResult:
    """Enhanced cross-platform correlation result"""
    primary_email: str
    primary_phone: Optional[str] = None
    profiles: Optional[List[ProfileData]] = None
    confidence_score: float = 0.0
    correlation_evidence: Optional[List[str]] = None
    best_profile_picture: Optional[str] = None
    activity_score: float = 0.0
    digital_footprint_score: float = 0.0
    risk_assessment: Optional[Dict[str, Any]] = None
    processed_at: Optional[datetime] = None
    platform_coverage: Optional[Dict[str, int]] = None

    def __post_init__(self):
        """Initialize default values"""
        if self.profiles is None:
            self.profiles = []
        if self.correlation_evidence is None:
            self.correlation_evidence = []
        if self.risk_assessment is None:
            self.risk_assessment = {}
        if self.platform_coverage is None:
            self.platform_coverage = {}
        if self.processed_at is None:
            self.processed_at = datetime.now()

class SocialAgent:
    """
    ENTERPRISE SOCIAL INTELLIGENCE AGENT v2.0
    Expanded coverage for 15+ platforms with specialized handling
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger("social_agent")
        
        # Initialize core components
        self.proxy_manager = ProxyManager()
        self.email_validator = EmailValidator()
        self.fuzzy_matcher = FuzzyMatcher()
        self.image_analyzer = ImageAnalyzer()
        self.strategy_router = StrategyRouter()
        self.activity_scorer = ActivityScorer()
        self.feedback_engine = FeedbackEngine()
        
        # Expanded agent registry
        self.platform_agents = {}
        self.platform_categories = {}
        self._init_expanded_agents()
        
        # Search state
        self.active_searches = {}
        self.rate_limit_tracker = {}
        
        self.logger.info("🤖 Social Agent Core v2.0 initialized with 15+ platform agents")
    
    def _init_expanded_agents(self):
        """Dynamically load expanded platform-specific agents"""
        try:
            # Professional Networks
            from agents.angellist_agent import AngelListAgent
            # Emerging Platforms
            from agents.bluesky_agent import BlueskyAgent
            from agents.discord_agent import DiscordAgent
            # Social Media
            from agents.facebook_agent import FacebookAgent
            from agents.flickr_agent import FlickrAgent
            # Code & Development
            from agents.github_agent import GitHubAgent
            from agents.gitlab_agent import GitLabAgent
            from agents.instagram_agent import InstagramAgent
            from agents.linkedin_agent import LinkedInAgent
            from agents.mastodon_agent import MastodonAgent
            # Specialized Platforms
            from agents.onlyfans_agent import OnlyFansAgent
            from agents.pinterest_agent import PinterestAgent
            from agents.reddit_agent import RedditAgent
            from agents.signal_agent import SignalAgent
            from agents.slack_agent import SlackAgent
            from agents.stackoverflow_agent import StackOverflowAgent
            # Messaging Apps (enhanced)
            from agents.telegram_agent import TelegramAgent
            from agents.threads_agent import ThreadsAgent
            from agents.tiktok_agent import TikTokAgent
            from agents.tumblr_agent import TumblrAgent
            from agents.twitter_agent import TwitterAgent
            from agents.whatsapp_agent import WhatsAppAgent
            from agents.xing_agent import XingAgent

            # Professional Agents
            self.platform_agents.update({
                'linkedin': LinkedInAgent(),
                'xing': XingAgent(),
                'angellist': AngelListAgent(),
            })
            
            # Social Media Agents
            self.platform_agents.update({
                'facebook': FacebookAgent(),
                'instagram': InstagramAgent(),
                'twitter': TwitterAgent(),
                'tiktok': TikTokAgent(),
                'pinterest': PinterestAgent(),
                'reddit': RedditAgent(),
            })
            
            # Messaging Agents
            self.platform_agents.update({
                'telegram': TelegramAgent(),
                'whatsapp': WhatsAppAgent(),
                'signal': SignalAgent(),
                'discord': DiscordAgent(),
                'slack': SlackAgent(),
            })
            
            # Code & Development Agents
            self.platform_agents.update({
                'github': GitHubAgent(),
                'gitlab': GitLabAgent(),
                'stackoverflow': StackOverflowAgent(),
            })
            
            # Emerging Platform Agents
            self.platform_agents.update({
                'bluesky': BlueskyAgent(),
                'threads': ThreadsAgent(),
                'mastodon': MastodonAgent(),
            })
            
            # Specialized Platform Agents
            self.platform_agents.update({
                'onlyfans': OnlyFansAgent(),
                'tumblr': TumblrAgent(),
                'flickr': FlickrAgent(),
            })
            
            # Define platform categories
            self.platform_categories = {
                PlatformCategory.PROFESSIONAL: ['linkedin', 'xing', 'angellist'],
                PlatformCategory.SOCIAL_MEDIA: ['facebook', 'instagram', 'twitter', 'tiktok', 'pinterest', 'reddit'],
                PlatformCategory.MESSAGING: ['telegram', 'whatsapp', 'signal', 'discord', 'slack'],
                PlatformCategory.CODE: ['github', 'gitlab', 'stackoverflow'],
                PlatformCategory.EMERGING: ['bluesky', 'threads', 'mastodon'],
                PlatformCategory.SPECIALIZED: ['onlyfans', 'tumblr', 'flickr']
            }
            
            self.logger.info(f"✅ Loaded {len(self.platform_agents)} platform agents across {len(self.platform_categories)} categories")
            
        except ImportError as e:
            self.logger.warning(f"⚠️ Some agents not available: {e}")
            self._create_expanded_stub_agents()
    
    def _create_expanded_stub_agents(self):
        """Create stub agents for all platforms for development"""
        from .base_agent import BaseAgent
        
        class StubAgent(BaseAgent):
            def __init__(self, platform: str, category: PlatformCategory):
                super().__init__()
                self.platform = platform
                self.category = category
            
            async def search_by_email(self, email: str, context: Dict = None) -> List[ProfileData]:
                self.logger.info(f"Stub agent {self.platform} searching for {email}")
                # Return mock data for development
                return []
            
            async def search_by_phone(self, phone: str, context: Dict = None) -> List[ProfileData]:
                self.logger.info(f"Stub agent {self.platform} searching for phone: {phone}")
                return []
        
        # Create stubs for all platforms
        all_platforms = {
            # Professional
            'linkedin': PlatformCategory.PROFESSIONAL,
            'xing': PlatformCategory.PROFESSIONAL,
            'angellist': PlatformCategory.PROFESSIONAL,
            # Social Media
            'facebook': PlatformCategory.SOCIAL_MEDIA,
            'instagram': PlatformCategory.SOCIAL_MEDIA,
            'twitter': PlatformCategory.SOCIAL_MEDIA,
            'tiktok': PlatformCategory.SOCIAL_MEDIA,
            'pinterest': PlatformCategory.SOCIAL_MEDIA,
            'reddit': PlatformCategory.SOCIAL_MEDIA,
            # Messaging
            'telegram': PlatformCategory.MESSAGING,
            'whatsapp': PlatformCategory.MESSAGING,
            'signal': PlatformCategory.MESSAGING,
            'discord': PlatformCategory.MESSAGING,
            'slack': PlatformCategory.MESSAGING,
            # Code
            'github': PlatformCategory.CODE,
            'gitlab': PlatformCategory.CODE,
            'stackoverflow': PlatformCategory.CODE,
            # Emerging
            'bluesky': PlatformCategory.EMERGING,
            'threads': PlatformCategory.EMERGING,
            'mastodon': PlatformCategory.EMERGING,
            # Specialized
            'onlyfans': PlatformCategory.SPECIALIZED,
            'tumblr': PlatformCategory.SPECIALIZED,
            'flickr': PlatformCategory.SPECIALIZED,
        }
        
        for platform, category in all_platforms.items():
            self.platform_agents[platform] = StubAgent(platform, category)
    
    async def _validate_inputs(self, email: str, user_context: Dict = None) -> None:
        """Validate input parameters"""
        if not email or not isinstance(email, str):
            raise ValidationError("Invalid email address provided")
        
        if not self.email_validator.validate(email):
            raise ValidationError(f"Invalid email format: {email}")
    
    async def process_email(self, email: str, user_context: Dict = None) -> CorrelationResult:
        """
        ENHANCED PROCESSING PIPELINE - Multi-platform intelligence gathering
        """
        search_id = f"{email}_{int(time.time())}"
        self.active_searches[search_id] = {
            'status': SearchStatus.IN_PROGRESS,
            'started_at': datetime.now(),
            'email': email
        }
        
        try:
            self.logger.info(f"🎯 Starting expanded social lookup for: {email}")
            
            # STEP 1: Enhanced Pre-processing & Validation
            await self._validate_inputs(email, user_context)
            
            # STEP 2: Multi-Category Platform Search
            primary_results = await self._execute_multi_category_search(email, user_context)
            
            # STEP 3: Advanced Cross-Platform Correlation
            correlated_results = await self._advanced_cross_correlate(email, primary_results, user_context)
            
            # STEP 4: Enhanced Confidence Scoring & Risk Assessment
            final_result = await self._calculate_enhanced_confidence(correlated_results, email)
            
            # STEP 5: Digital Footprint Analysis
            await self._analyze_digital_footprint(final_result)
            
            # STEP 6: Continuous Learning
            await self._update_feedback_engine(final_result)
            
            self.active_searches[search_id]['status'] = SearchStatus.COMPLETED
            self.logger.info(f"✅ Expanded search completed for {email} - Confidence: {final_result.confidence_score:.2f}")
            
            return final_result
            
        except Exception as e:
            self.active_searches[search_id]['status'] = SearchStatus.FAILED
            self.active_searches[search_id]['error'] = str(e)
            self.logger.error(f"❌ Expanded search failed for {email}: {e}")
            raise
    
    async def process_phone(self, phone: str, user_context: Dict = None) -> CorrelationResult:
        """
        PROCESS PHONE NUMBER - Specialized handling for messaging apps
        """
        search_id = f"phone_{phone}_{int(time.time())}"
        self.active_searches[search_id] = {
            'status': SearchStatus.IN_PROGRESS,
            'started_at': datetime.now(),
            'phone': phone
        }
        
        try:
            self.logger.info(f"📱 Starting phone-based lookup for: {phone}")
            
            # Validate phone format
            if not self._validate_phone_format(phone):
                raise ValidationError(f"Invalid phone format: {phone}")
            
            # Focus on messaging platforms for phone lookup
            messaging_results = await self._execute_messaging_platform_search(phone, user_context)
            
            # Also try email lookup if we can derive email from phone
            potential_emails = await self._derive_emails_from_phone(phone)
            email_results = {}
            
            for email in potential_emails:
                try:
                    email_search_results = await self._execute_multi_category_search(email, user_context)
                    email_results[email] = email_search_results
                except Exception as e:
                    self.logger.warning(f"⚠️ Email derivation search failed for {email}: {e}")
            
            # Combine all results
            all_profiles = []
            for platform_profiles in messaging_results.values():
                all_profiles.extend(platform_profiles)
            
            for email_result in email_results.values():
                for platform_profiles in email_result.values():
                    all_profiles.extend(platform_profiles)
            
            # Deduplicate and correlate
            unique_profiles = await self._deduplicate_profiles(all_profiles)
            final_result = await self._calculate_enhanced_confidence(unique_profiles, primary_phone=phone)
            final_result.primary_phone = phone
            
            self.active_searches[search_id]['status'] = SearchStatus.COMPLETED
            return final_result
            
        except Exception as e:
            self.active_searches[search_id]['status'] = SearchStatus.FAILED
            self.active_searches[search_id]['error'] = str(e)
            raise
    
    def _validate_phone_format(self, phone: str) -> bool:
        """Validate international phone number format"""
        import re

        # Basic international format validation
        pattern = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))
    
    async def _derive_emails_from_phone(self, phone: str) -> List[str]:
        """Derive potential email addresses from phone number"""
        # Remove country code and special characters
        clean_phone = phone.lstrip('+').replace(' ', '').replace('-', '')
        
        # Common email patterns from phone numbers
        patterns = [
            f"{clean_phone}@gmail.com",
            f"user{clean_phone}@gmail.com", 
            f"phone{clean_phone}@gmail.com",
            f"{clean_phone}@yahoo.com",
            f"{clean_phone}@outlook.com",
        ]
        
        return patterns
    
    async def _execute_multi_category_search(self, email: str, user_context: Dict) -> Dict[str, List[ProfileData]]:
        """
        Execute search across all platform categories with priority scheduling
        """
        self.logger.info("🌐 Executing multi-category platform search...")
        
        platform_results = {}
        search_strategies = self.strategy_router.get_multi_category_strategies(email, user_context)
        
        # Execute searches by category priority
        category_priority = [
            PlatformCategory.PROFESSIONAL,  # Highest confidence data
            PlatformCategory.CODE,          # Developer profiles
            PlatformCategory.SOCIAL_MEDIA,  # Main social platforms
            PlatformCategory.MESSAGING,     # Communication apps
            PlatformCategory.EMERGING,      # New platforms
            PlatformCategory.SPECIALIZED,   # Niche platforms
        ]
        
        for category in category_priority:
            category_platforms = self.platform_categories.get(category, [])
            category_tasks = []
            
            for platform in category_platforms:
                if platform in search_strategies and platform in self.platform_agents:
                    task = self._search_platform_with_proxy(
                        platform, email, search_strategies[platform], user_context
                    )
                    category_tasks.append(task)
            
            # Execute category searches concurrently
            if category_tasks:
                self.logger.info(f"🔍 Searching {category.value} platforms...")
                results = await asyncio.gather(*category_tasks, return_exceptions=True)
                
                for platform, result in zip(category_platforms, results):
                    if not isinstance(result, Exception) and result is not None:
                        platform_results[platform] = result
        
        self.logger.info(f"✅ Multi-category search completed: {self._count_profiles(platform_results)} profiles across {len(platform_results)} platforms")
        return platform_results
    
    def _count_profiles(self, platform_results: Dict[str, List[ProfileData]]) -> int:
        """Count total profiles in platform results"""
        return sum(len(profiles) for profiles in platform_results.values())
    
    async def _search_platform_with_proxy(self, platform: str, email: str, strategy: Dict, user_context: Dict) -> List[ProfileData]:
        """Execute platform search with proxy rotation"""
        agent = self.platform_agents[platform]
        max_retries = getattr(self.settings.agents, 'MAX_RETRIES', 3)
        
        for attempt in range(max_retries):
            try:
                proxy = self.proxy_manager.get_proxy()
                if proxy:
                    agent.set_proxy(proxy)
                
                results = await agent.search_by_email(email, strategy, user_context)
                
                self.logger.info(f"✅ {platform} search found {len(results)} profiles")
                return results
                
            except Exception as e:
                self.logger.warning(f"⚠️ {platform} search error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
          
