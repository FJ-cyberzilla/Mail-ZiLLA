"""
SOCIAL AGENT CORE - Enterprise Intelligence Engine v4.0
Advanced Browser Fingerprinting & System Intelligence Integration
"""

import asyncio
import time
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import platform
import uuid

# New imports for advanced capabilities
from .browser_fingerprinter import BrowserFingerprinter
from .system_intelligence import SystemIntelligence
from .network_analyzer import NetworkAnalyzer
from .hardware_profiler import HardwareProfiler
from .behavioral_analyzer import BehavioralAnalyzer

# ... [previous imports remain]

@dataclass
class DigitalFootprint:
    """Comprehensive digital footprint analysis"""
    profiles: List[ProfileData]
    browser_fingerprint: Dict[str, Any]
    system_profile: Dict[str, Any]
    network_characteristics: Dict[str, Any]
    hardware_profile: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]
    confidence_score: float
    risk_assessment: Dict[str, Any]
    unique_identifiers: List[str]

@dataclass
class AdvancedCorrelationResult:
    """Enhanced correlation with digital fingerprinting"""
    primary_email: str
    primary_phone: Optional[str]
    profiles: List[ProfileData]
    digital_footprint: DigitalFootprint
    confidence_score: float
    correlation_evidence: List[str]
    behavioral_analysis: Dict[str, Any]
    system_intelligence: Dict[str, Any]
    processed_at: datetime

class SocialAgent:
    """
    ENTERPRISE SOCIAL INTELLIGENCE AGENT v4.0
    Advanced browser fingerprinting, system intelligence, and behavioral analysis
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
        
        # Advanced intelligence components
        self.browser_fingerprinter = BrowserFingerprinter()
        self.system_intelligence = SystemIntelligence()
        self.network_analyzer = NetworkAnalyzer()
        self.hardware_profiler = HardwareProfiler()
        self.behavioral_analyzer = BehavioralAnalyzer()
        
        # Complete agent registry
        self.platform_agents = {}
        self.platform_categories = {}
        self._init_complete_agents()
        
        # Search state
        self.active_searches = {}
        self.rate_limit_tracker = {}
        
        self.logger.info("🤖 Social Agent Core v4.0 initialized with advanced fingerprinting capabilities")
    
    async def process_email_advanced(self, email: str, user_context: Dict = None, 
                                   collect_fingerprint: bool = True) -> AdvancedCorrelationResult:
        """
        ADVANCED PROCESSING with digital fingerprinting and system intelligence
        """
        search_id = f"adv_{email}_{int(time.time())}"
        self.active_searches[search_id] = {
            'status': SearchStatus.IN_PROGRESS,
            'started_at': datetime.now(),
            'email': email,
            'advanced_mode': True
        }
        
        try:
            self.logger.info(f"🎯 Starting advanced intelligence gathering for: {email}")
            
            # STEP 1: Enhanced Pre-processing with System Intelligence
            await self._validate_inputs(email, user_context)
            
            # STEP 2: Collect Digital Footprint (if enabled)
            digital_footprint = None
            if collect_fingerprint:
                digital_footprint = await self._collect_digital_footprint(email, user_context)
            
            # STEP 3: Multi-Platform Intelligence Gathering
            platform_results = await self._execute_multi_category_search(email, user_context)
            
            # STEP 4: Behavioral Analysis Integration
            behavioral_analysis = await self._analyze_behavioral_patterns(platform_results, digital_footprint)
            
            # STEP 5: Advanced Cross-Platform Correlation with Fingerprinting
            correlated_results = await self._fingerprint_enhanced_correlation(email, platform_results, digital_footprint)
            
            # STEP 6: System Intelligence Integration
            system_intel = await self._gather_system_intelligence(correlated_results, digital_footprint)
            
            # STEP 7: Calculate Enhanced Confidence with Fingerprinting
            final_result = await self._calculate_fingerprint_enhanced_confidence(
                correlated_results, digital_footprint, behavioral_analysis
            )
            
            self.active_searches[search_id]['status'] = SearchStatus.COMPLETED
            self.logger.info(f"✅ Advanced search completed for {email} - Confidence: {final_result.confidence_score:.2f}")
            
            return final_result
            
        except Exception as e:
            self.active_searches[search_id]['status'] = SearchStatus.FAILED
            self.active_searches[search_id]['error'] = str(e)
            self.logger.error(f"❌ Advanced search failed for {email}: {e}")
            raise
    
    async def _collect_digital_footprint(self, email: str, user_context: Dict) -> DigitalFootprint:
        """
        Collect comprehensive digital footprint using advanced techniques
        """
        self.logger.info("🔍 Collecting digital footprint...")
        
        # Collect all intelligence data concurrently
        fingerprint_tasks = [
            self.browser_fingerprinter.collect_fingerprint(),
            self.system_intelligence.gather_system_info(),
            self.network_analyzer.analyze_network_characteristics(),
            self.hardware_profiler.profile_hardware(),
            self.behavioral_analyzer.analyze_behavioral_patterns(email)
        ]
        
        results = await asyncio.gather(*fingerprint_tasks, return_exceptions=True)
        
        # Process results
        browser_fp = results[0] if not isinstance(results[0], Exception) else {}
        system_info = results[1] if not isinstance(results[1], Exception) else {}
        network_info = results[2] if not isinstance(results[2], Exception) else {}
        hardware_info = results[3] if not isinstance(results[3], Exception) else {}
        behavioral_info = results[4] if not isinstance(results[4], Exception) else {}
        
        # Generate unique identifiers from fingerprint
        unique_identifiers = self._generate_unique_identifiers(
            browser_fp, system_info, network_info
        )
        
        # Calculate initial confidence
        confidence_score = self._calculate_fingerprint_confidence(
            browser_fp, system_info, network_info
        )
        
        footprint = DigitalFootprint(
            profiles=[],
            browser_fingerprint=browser_fp,
            system_profile=system_info,
            network_characteristics=network_info,
            hardware_profile=hardware_info,
            behavioral_patterns=behavioral_info,
            confidence_score=confidence_score,
            risk_assessment={},
            unique_identifiers=unique_identifiers
        )
        
        self.logger.info(f"✅ Digital footprint collected: {len(unique_identifiers)} unique identifiers")
        return footprint
    
    def _generate_unique_identifiers(self, browser_fp: Dict, system_info: Dict, network_info: Dict) -> List[str]:
        """Generate unique identifiers from fingerprint data"""
        identifiers = []
        
        # Browser canvas fingerprint
        if 'canvas_fingerprint' in browser_fp:
            identifiers.append(f"canvas_{browser_fp['canvas_fingerprint']}")
        
        # WebGL fingerprint
        if 'webgl_fingerprint' in browser_fp:
            identifiers.append(f"webgl_{browser_fp['webgl_fingerprint']}")
        
        # Audio context fingerprint
        if 'audio_fingerprint' in browser_fp:
            identifiers.append(f"audio_{browser_fp['audio_fingerprint']}")
        
        # System hardware identifiers
        if 'hardware_concurrency' in system_info:
            identifiers.append(f"cpu_cores_{system_info['hardware_concurrency']}")
        
        if 'device_memory' in system_info:
            identifiers.append(f"ram_{system_info['device_memory']}")
        
        # Screen characteristics
        if 'screen_resolution' in system_info:
            identifiers.append(f"screen_{system_info['screen_resolution']}")
        
        # Timezone and locale
        if 'timezone' in system_info:
            identifiers.append(f"tz_{system_info['timezone']}")
        
        if 'language' in system_info:
            identifiers.append(f"lang_{system_info['language']}")
        
        # Battery characteristics (if available)
        if 'battery_level' in system_info:
            identifiers.append(f"battery_{system_info['battery_level']}")
        
        # Network characteristics
        if 'ip_address' in network_info:
            identifiers.append(f"ip_{hashlib.md5(network_info['ip_address'].encode()).hexdigest()[:8]}")
        
        if 'network_type' in network_info:
            identifiers.append(f"net_{network_info['network_type']}")
        
        return identifiers
    
    def _calculate_fingerprint_confidence(self, browser_fp: Dict, system_info: Dict, network_info: Dict) -> float:
        """Calculate confidence based on fingerprint quality and uniqueness"""
        confidence_factors = []
        
        # Browser fingerprint completeness
        browser_fields = ['canvas_fingerprint', 'webgl_fingerprint', 'user_agent', 'plugins']
        browser_completeness = sum(1 for field in browser_fields if field in browser_fp) / len(browser_fields)
        confidence_factors.append(browser_completeness * 0.3)
        
        # System information completeness
        system_fields = ['platform', 'hardware_concurrency', 'device_memory', 'screen_resolution']
        system_completeness = sum(1 for field in system_fields if field in system_info) / len(system_fields)
        confidence_factors.append(system_completeness * 0.3)
        
        # Network information
        if 'ip_address' in network_info:
            confidence_factors.append(0.2)
        
        # Fingerprint uniqueness indicators
        uniqueness_indicators = 0
        if browser_fp.get('canvas_fingerprint'):
            uniqueness_indicators += 1
        if browser_fp.get('webgl_fingerprint'):
            uniqueness_indicators += 1
        if browser_fp.get('audio_fingerprint'):
            uniqueness_indicators += 1
        
        confidence_factors.append((uniqueness_indicators / 3) * 0.2)
        
        return sum(confidence_factors)
    
    async def _analyze_behavioral_patterns(self, platform_results: Dict[str, List[ProfileData]], 
                                         digital_footprint: DigitalFootprint) -> Dict[str, Any]:
        """Analyze behavioral patterns across platforms"""
        behavioral_analysis = {
            'platform_usage_patterns': {},
            'activity_consistency': {},
            'content_preferences': {},
            'temporal_patterns': {},
            'risk_indicators': []
        }
        
        # Analyze platform usage patterns
        platform_activity = {}
        for platform, profiles in platform_results.items():
            if profiles:
                latest_activity = max(p.last_activity for p in profiles if p.last_activity)
                platform_activity[platform] = latest_activity
        
        behavioral_analysis['platform_usage_patterns'] = platform_activity
        
        # Check for behavioral red flags
        risk_indicators = await self._identify_behavioral_risks(platform_results, digital_footprint)
        behavioral_analysis['risk_indicators'] = risk_indicators
        
        # Analyze content preferences
        content_analysis = await self._analyze_content_preferences(platform_results)
        behavioral_analysis['content_preferences'] = content_analysis
        
        return behavioral_analysis
    
    async def _identify_behavioral_risks(self, platform_results: Dict[str, List[ProfileData]], 
                                       digital_footprint: DigitalFootprint) -> List[Dict[str, Any]]:
        """Identify potential behavioral risk indicators"""
        risks = []
        
        # Check for platform inconsistency
        professional_platforms = ['linkedin', 'xing', 'glassdoor']
        anonymous_platforms = ['reddit', '4chan', 'telegram']
        
        has_professional = any(platform in professional_platforms for platform in platform_results.keys())
        has_anonymous = any(platform in anonymous_platforms for platform in platform_results.keys())
        
        if has_professional and has_anonymous:
            risks.append({
                'type': 'PLATFORM_IDENTITY_DICHOTOMY',
                'level': 'MEDIUM',
                'description': 'Active on both professional and anonymous platforms',
                'confidence': 0.7
            })
        
        # Check for activity time patterns
        activity_times = await self._analyze_activity_timing(platform_results)
        if activity_times.get('nocturnal_activity', 0) > 0.6:  # 60%+ activity during night
            risks.append({
                'type': 'NOCTURNAL_ACTIVITY_PATTERN',
                'level': 'LOW',
                'description': 'Significant activity during late night hours',
                'confidence': 0.6
            })
        
        return risks
    
    async def _analyze_activity_timing(self, platform_results: Dict[str, List[ProfileData]]) -> Dict[str, float]:
        """Analyze temporal activity patterns"""
        activity_hours = {hour: 0 for hour in range(24)}
        total_activities = 0
        
        for platform, profiles in platform_results.items():
            for profile in profiles:
                if profile.last_activity:
                    hour = profile.last_activity.hour
                    activity_hours[hour] += 1
                    total_activities += 1
        
        if total_activities == 0:
            return {}
        
        # Normalize activity distribution
        activity_distribution = {hour: count/total_activities for hour, count in activity_hours.items()}
        
        # Calculate patterns
        daytime_activity = sum(activity_distribution[hour] for hour in range(8, 20))  # 8 AM - 8 PM
        nighttime_activity = sum(activity_distribution[hour] for hour in list(range(0, 8)) + list(range(20, 24)))
        
        return {
            'daytime_activity': daytime_activity,
            'nighttime_activity': nighttime_activity,
            'nocturnal_activity': nighttime_activity,
            'peak_hours': sorted(activity_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    async def _analyze_content_preferences(self, platform_results: Dict[str, List[ProfileData]]) -> Dict[str, Any]:
        """Analyze content and interest preferences across platforms"""
        interests = set()
        professional_interests = set()
        personal_interests = set()
        
        for platform, profiles in platform_results.items():
            for profile in profiles:
                if profile.bio:
                    # Simple keyword extraction (in practice, use NLP)
                    bio_lower = profile.bio.lower()
                    
                    # Professional interests
                    professional_keywords = ['developer', 'engineer', 'designer', 'manager', 'director', 
                                           'software', 'marketing', 'sales', 'finance', 'hr']
                    for keyword in professional_keywords:
                        if keyword in bio_lower:
                            professional_interests.add(keyword)
                    
                    # Personal interests
                    personal_keywords = ['gaming', 'music', 'travel', 'food', 'fitness', 'sports',
                                       'photography', 'reading', 'art', 'technology']
                    for keyword in personal_keywords:
                        if keyword in bio_lower:
                            personal_interests.add(keyword)
        
        return {
            'professional_interests': list(professional_interests),
            'personal_interests': list(personal_interests),
            'total_interest_categories': len(professional_interests) + len(personal_interests)
        }
    
    async def _fingerprint_enhanced_correlation(self, email: str, 
                                              platform_results: Dict[str, List[ProfileData]],
                                              digital_footprint: DigitalFootprint) -> List[ProfileData]:
        """
        Enhanced correlation using digital fingerprinting data
        """
        all_profiles = []
        
        # Add primary results
        for platform_profiles in platform_results.values():
            all_profiles.extend(platform_profiles)
        
        # Use fingerprint data to enhance correlation
        if digital_footprint and digital_footprint.unique_identifiers:
            enhanced_results = await self._execute_fingerprint_enhanced_searches(
                email, digital_footprint, platform_results
            )
            for platform_profiles in enhanced_results.values():
                all_profiles.extend(platform_profiles)
        
        # Advanced deduplication with fingerprint context
        unique_profiles = await self._fingerprint_aware_deduplication(all_profiles, digital_footprint)
        
        return unique_profiles
    
    async def _execute_fingerprint_enhanced_searches(self, email: str, 
                                                   digital_footprint: DigitalFootprint,
                                                   existing_results: Dict[str, List[ProfileData]]) -> Dict[str, List[ProfileData]]:
        """Execute searches enhanced with fingerprint data"""
        enhanced_results = {}
        
        # Use fingerprint data to refine search strategies
        fingerprint_strategies = self.strategy_router.get_fingerprint_enhanced_strategies(
            email, digital_footprint, existing_results
        )
        
        search_tasks = []
        for platform, strategy in fingerprint_strategies.items():
            if platform in self.platform_agents:
                task = self._search_platform_with_fingerprint_context(
                    platform, email, strategy, digital_footprint
                )
                search_tasks.append(task)
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        for platform, result in zip(fingerprint_strategies.keys(), results):
            if not isinstance(result, Exception):
                enhanced_results[platform] = result
        
        return enhanced_results
    
    async def _gather_system_intelligence(self, profiles: List[ProfileData], 
                                        digital_footprint: DigitalFootprint) -> Dict[str, Any]:
        """Gather comprehensive system intelligence"""
        system_intel = {
            'device_characteristics': {},
            'network_analysis': {},
            'security_posture': {},
            'privacy_indicators': {}
        }
        
        if digital_footprint:
            # Analyze device characteristics
            system_intel['device_characteristics'] = {
                'device_type': self._infer_device_type(digital_footprint.system_profile),
                'likely_operating_system': digital_footprint.system_profile.
