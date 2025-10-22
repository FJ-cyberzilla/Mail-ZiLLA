"""
ENTERPRISE DECEPTION DETECTION SYSTEM
Advanced detection of shared accounts, timezone manipulation, and identity obfuscation
"""

import asyncio
import hashlib
import json
import re
import statistics
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class DeceptionType(Enum):
    SHARED_ACCOUNT = "shared_account"
    TIMEZONE_MANIPULATION = "timezone_manipulation"
    IDENTITY_FRAGMENTATION = "identity_fragmentation"
    PROFILE_SPOOFING = "profile_spoofing"
    ACTIVITY_PATTERN_ANOMALY = "activity_pattern_anomaly"
    HARDWARE_SPOOFING = "hardware_spoofing"
    BEHAVIORAL_INCONSISTENCY = "behavioral_inconsistency"

@dataclass
class DeceptionIndicator:
    type: DeceptionType
    confidence: float
    evidence: List[str]
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    impact_score: float

@dataclass
class DeceptionAnalysis:
    overall_risk_score: float
    deception_indicators: List[DeceptionIndicator]
    recommended_actions: List[str]
    confidence_level: str
    anomaly_count: int

class DeceptionDetector:
    """
    ENTERPRISE DECEPTION DETECTION ENGINE
    Advanced detection of manipulation techniques and shared account usage
    """
    
    def __init__(self):
        self.logger = logging.getLogger("deception_detector")
        
        # Pattern databases
        self.shared_account_patterns = self._load_shared_account_patterns()
        self.timezone_anomaly_rules = self._load_timezone_anomaly_rules()
        self.spoofing_indicators = self._load_spoofing_indicators()
        
        # Behavioral baselines
        self.behavioral_baselines = self._initialize_behavioral_baselines()
        
        self.logger.info("🕵️ Enterprise Deception Detector initialized")
    
    async def analyze_digital_identity(self, profiles: List[ProfileData], 
                                     digital_footprint: DigitalFootprint,
                                     behavioral_analysis: Dict[str, Any]) -> DeceptionAnalysis:
        """
        Comprehensive deception analysis across all identity dimensions
        """
        deception_indicators = []
        
        # Run all deception detection modules
        detection_tasks = [
            self._detect_shared_accounts(profiles, behavioral_analysis),
            self._detect_timezone_manipulation(digital_footprint, behavioral_analysis),
            self._detect_identity_fragmentation(profiles),
            self._detect_profile_spoofing(profiles, digital_footprint),
            self._detect_activity_anomalies(behavioral_analysis),
            self._detect_hardware_spoofing(digital_footprint),
            self._detect_behavioral_inconsistencies(profiles, behavioral_analysis)
        ]
        
        results = await asyncio.gather(*detection_tasks)
        
        # Collect all indicators
        for result in results:
            if result:
                deception_indicators.extend(result)
        
        # Calculate overall risk score
        overall_risk = self._calculate_overall_risk(deception_indicators)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(deception_indicators)
        
        return DeceptionAnalysis(
            overall_risk_score=overall_risk,
            deception_indicators=deception_indicators,
            recommended_actions=recommendations,
            confidence_level=self._determine_confidence_level(deception_indicators),
            anomaly_count=len(deception_indicators)
        )
    
    async def _detect_shared_accounts(self, profiles: List[ProfileData], 
                                    behavioral_analysis: Dict[str, Any]) -> List[DeceptionIndicator]:
        """
        Detect shared account usage through multi-dimensional analysis
        """
        indicators = []
        evidence = []
        confidence = 0.0
        
        # 1. Username Pattern Analysis
        username_analysis = await self._analyze_username_patterns(profiles)
        if username_analysis['suspicious_patterns']:
            evidence.extend(username_analysis['suspicious_patterns'])
            confidence += 0.3
        
        # 2. Activity Pattern Analysis
        activity_analysis = await self._analyze_activity_patterns(behavioral_analysis)
        if activity_analysis['multiple_behavioral_profiles']:
            evidence.append("Multiple distinct behavioral patterns detected")
            confidence += 0.4
        
        # 3. Content Style Analysis
        content_analysis = await self._analyze_content_style(profiles)
        if content_analysis['style_variations']:
            evidence.append(f"Multiple writing styles detected: {content_analysis['style_variations']} variations")
            confidence += 0.3
        
        # 4. Geographic Inconsistency
        geo_analysis = await self._analyze_geographic_consistency(profiles)
        if geo_analysis['geographic_spread']:
            evidence.append(f"Activity from {geo_analysis['geographic_spread']} distinct geographic regions")
            confidence += 0.2
        
        if evidence and confidence > 0.5:
            indicators.append(DeceptionIndicator(
                type=DeceptionType.SHARED_ACCOUNT,
                confidence=min(confidence, 0.95),
                evidence=evidence,
                severity=self._calculate_severity(confidence),
                impact_score=0.8
            ))
        
        return indicators
    
    async def _analyze_username_patterns(self, profiles: List[ProfileData]) -> Dict[str, Any]:
        """Analyze username patterns for shared account indicators"""
        analysis = {
            'suspicious_patterns': [],
            'username_entropy': 0.0,
            'pattern_consistency': 0.0
        }
        
        usernames = [p.username for p in profiles if p.username]
        
        if len(usernames) < 2:
            return analysis
        
        # Check for generic/shared account patterns
        generic_patterns = [
            r'.*team$', r'.*group$', r'.*office$', r'.*company$',
            r'^info\.', r'^admin\.', r'^contact\.', r'^hello\.',
            r'.*[\d]{4,}',  # Many numbers (shared office accounts)
            r'^weare\.', r'^our\.', r'^the\.'
        ]
        
        for username in usernames:
            for pattern in generic_patterns:
                if re.match(pattern, username, re.IGNORECASE):
                    analysis['suspicious_patterns'].append(f"Generic username pattern: {username}")
                    break
        
        # Analyze username entropy (low entropy = potentially shared)
        entropy_scores = [self._calculate_entropy(username) for username in usernames]
        avg_entropy = statistics.mean(entropy_scores) if entropy_scores else 0
        
        if avg_entropy < 2.5:  # Low entropy threshold
            analysis['suspicious_patterns'].append(f"Low username entropy: {avg_entropy:.2f}")
        
        return analysis
    
    async def _analyze_activity_patterns(self, behavioral_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze activity patterns for multiple user behaviors"""
        analysis = {
            'multiple_behavioral_profiles': False,
            'temporal_clusters': 0,
            'activity_variance': 0.0
        }
        
        activity_data = behavioral_analysis.get('platform_usage_patterns', {})
        
        if len(activity_data) < 3:
            return analysis
        
        # Analyze activity timing for multiple patterns
        activity_hours = []
        for platform, last_activity in activity_data.items():
            if last_activity:
                activity_hours.append(last_activity.hour)
        
        if len(activity_hours) >= 3:
            # Check for multiple temporal clusters
            hour_clusters = self._cluster_activity_hours(activity_hours)
            if len(hour_clusters) >= 2:
                analysis['multiple_behavioral_profiles'] = True
                analysis['temporal_clusters'] = len(hour_clusters)
        
        return analysis
    
    async def _analyze_content_style(self, profiles: List[ProfileData]) -> Dict[str, Any]:
        """Analyze content style variations across platforms"""
        analysis = {
            'style_variations': 0,
            'formality_variance': 0.0,
            'vocabulary_diversity': 0.0
        }
        
        bios = [p.bio for p in profiles if p.bio and len(p.bio) > 10]
        
        if len(bios) < 2:
            return analysis
        
        # Analyze formality levels
        formality_scores = []
        for bio in bios:
            formality_scores.append(self._calculate_formality_score(bio))
        
        formality_variance = statistics.variance(formality_scores) if len(formality_scores) > 1 else 0
        
        if formality_variance > 0.3:  # High variance in formality
            analysis['style_variations'] = len(set(round(score, 1) for score in formality_scores))
            analysis['formality_variance'] = formality_variance
        
        return analysis
    
    async def _analyze_geographic_consistency(self, profiles: List[ProfileData]) -> Dict[str, Any]:
        """Analyze geographic consistency across profiles"""
        analysis = {
            'geographic_spread': 0,
            'timezone_consistency': 0.0,
            'location_conflicts': []
        }
        
        locations = [p.location for p in profiles if p.location]
        unique_locations = set(locations)
        
        if len(unique_locations) > 2:  # More than 2 distinct locations
            analysis['geographic_spread'] = len(unique_locations)
        
        return analysis
    
    async def _detect_timezone_manipulation(self, digital_footprint: DigitalFootprint,
                                          behavioral_analysis: Dict[str, Any]) -> List[DeceptionIndicator]:
        """
        Detect timezone manipulation and location spoofing
        """
        indicators = []
        evidence = []
        confidence = 0.0
        
        system_tz = digital_footprint.system_profile.get('timezone', '')
        ip_geolocation = digital_footprint.network_characteristics.get('ip_geolocation', {})
        
        # 1. System vs IP Timezone Mismatch
        if system_tz and ip_geolocation.get('timezone'):
            if system_tz != ip_geolocation.get('timezone'):
                evidence.append(f"Timezone mismatch: System={system_tz}, IP={ip_geolocation.get('timezone')}")
                confidence += 0.6
        
        # 2. Activity vs Declared Timezone Analysis
        activity_analysis = await self._analyze_activity_vs_timezone(behavioral_analysis, system_tz)
        if activity_analysis['anomalous_activity']:
            evidence.extend(activity_analysis['anomalous_activity'])
            confidence += 0.4
        
        # 3. Timezone Consistency Check
        tz_consistency = await self._check_timezone_consistency(digital_footprint)
        if not tz_consistency['consistent']:
            evidence.append("Multiple timezone indicators detected")
            confidence += 0.3
        
        # 4. DST (Daylight Saving Time) Anomalies
        dst_anomalies = await self._detect_dst_anomalies(behavioral_analysis, system_tz)
        if dst_anomalies:
            evidence.append("Daylight Saving Time anomalies detected")
            confidence += 0.2
        
        if evidence and confidence > 0.5:
            indicators.append(DeceptionIndicator(
                type=DeceptionType.TIMEZONE_MANIPULATION,
                confidence=min(confidence, 0.95),
                evidence=evidence,
                severity=self._calculate_severity(confidence),
                impact_score=0.6
            ))
        
        return indicators
    
    async def _analyze_activity_vs_timezone(self, behavioral_analysis: Dict[str, Any], 
                                          system_timezone: str) -> Dict[str, Any]:
        """Analyze if activity patterns match declared timezone"""
        analysis = {'anomalous_activity': []}
        
        if not system_timezone:
            return analysis
        
        # Get timezone offset
        tz_offset = self._get_timezone_offset(system_timezone)
        
        # Analyze activity hours relative to timezone
        activity_data = behavioral_analysis.get('platform_usage_patterns', {})
        activity_hours = []
        
        for platform, last_activity in activity_data.items():
            if last_activity:
                # Convert to declared timezone
                localized_hour = (last_activity.hour + tz_offset) % 24
                activity_hours.append(localized_hour)
        
        if activity_hours:
            # Check for activity during unusual hours for timezone
            night_activity = sum(1 for hour in activity_hours if hour < 6 or hour > 22)
            if night_activity / len(activity_hours) > 0.7:  # 70%+ activity at night
                analysis['anomalous_activity'].append("High nighttime activity for declared timezone")
        
        return analysis
    
    async def _check_timezone_consistency(self, digital_footprint: DigitalFootprint) -> Dict[str, Any]:
        """Check consistency across multiple timezone indicators"""
        analysis = {'consistent': True, 'conflicts': []}
        
        system_tz = digital_footprint.system_profile.get('timezone')
        ip_tz = digital_footprint.network_characteristics.get('ip_geolocation', {}).get('timezone')
        browser_tz = digital_footprint.browser_fingerprint.get('timezone')
        
        timezones = [tz for tz in [system_tz, ip_tz, browser_tz] if tz]
        
        if len(set(timezones)) > 1:
            analysis['consistent'] = False
            analysis['conflicts'] = list(set(timezones))
        
        return analysis
    
    async def _detect_dst_anomalies(self, behavioral_analysis: Dict[str, Any], 
                                  system_timezone: str) -> bool:
        """Detect Daylight Saving Time anomalies"""
        if not system_timezone:
            return False
        
        # Check if timezone observes DST
        observes_dst = self._timezone_observes_dst(system_timezone)
        
        if observes_dst:
            # Analyze activity around DST transitions
            activity_data = behavioral_analysis.get('platform_usage_patterns', {})
            # Implementation would check for activity pattern disruptions during DST changes
        
        return False  # Placeholder
    
    async def _detect_identity_fragmentation(self, profiles: List[ProfileData]) -> List[DeceptionIndicator]:
        """
        Detect intentional identity fragmentation across platforms
        """
        indicators = []
        evidence = []
        confidence = 0.0
        
        # 1. Name Variation Analysis
        name_analysis = await self._analyze_name_variations(profiles)
        if name_analysis['excessive_variations']:
            evidence.append(f"Excessive name variations: {name_analysis['variation_count']} different names")
            confidence += 0.4
        
        # 2. Profile Completeness Analysis
        completeness_analysis = await self._analyze_profile_completeness(profiles)
        if completeness_analysis['incomplete_pattern']:
            evidence.append("Strategic profile incompleteness detected")
            confidence += 0.3
        
        # 3. Platform Specialization Analysis
        specialization_analysis = await self._analyze_platform_specialization(profiles)
        if specialization_analysis['compartmentalized_identity']:
            evidence.append("Compartmentalized identity across platforms")
            confidence += 0.3
        
        if evidence and confidence > 0.4:
            indicators.append(DeceptionIndicator(
                type=DeceptionType.IDENTITY_FRAGMENTATION,
                confidence=min(confidence, 0.9),
                evidence=evidence,
                severity=self._calculate_severity(confidence),
                impact_score=0.7
            ))
        
        return indicators
    
    async def _analyze_name_variations(self, profiles: List[ProfileData]) -> Dict[str, Any]:
        """Analyze name variations for intentional fragmentation"""
        analysis = {
            'excessive_variations': False,
            'variation_count': 0,
            'name_consistency_score': 0.0
        }
        
        names = [p.full_name for p in profiles if p.full_name]
        unique_names = set(names)
        
        if len(unique_names) > 3:  # More than 3 different names
            analysis['excessive_variations'] = True
            analysis['variation_count'] = len(unique_names)
        
        return analysis
    
    async def _analyze_profile_completeness(self, profiles: List[ProfileData]) -> Dict[str, Any]:
        """Analyze strategic profile incompleteness"""
        analysis = {
            'incomplete_pattern': False,
            'completeness_scores': [],
            'strategic_omissions': []
        }
        
        for profile in profiles:
            completeness = self._calculate_profile_completeness(profile)
            analysis['completeness_scores'].append(completeness)
        
        avg_completeness = statistics.mean(analysis['completeness_scores']) if analysis['completeness_scores'] else 0
        
        # Check for pattern of strategic omissions
        if avg_completeness < 0.3 and len(profiles) > 2:
            analysis['incomplete_pattern'] = True
        
        return analysis
    
    async def _analyze_platform_specialization(self, profiles: List[ProfileData]) -> Dict[str, Any]:
        """Analyze compartmentalized identity across platforms"""
        analysis = {
            'compartmentalized_identity': False,
            'platform_personas': {}
        }
        
        # Group profiles by platform category and analyze content focus
        for profile in profiles:
            category = profile.platform_category.value
            if category not in analysis['platform_personas']:
                analysis['platform_personas'][category] = []
            analysis['platform_personas'][category].append(profile)
        
        # Check for completely different personas across categories
        if len(analysis['platform_personas']) >= 3:
            # Analyze if different categories show different identity aspects
            analysis['compartmentalized_identity'] = True
        
        return analysis
    
    async def _detect_profile_spoofing(self, profiles: List[ProfileData], 
                                     digital_footprint: DigitalFootprint) -> List[DeceptionIndicator]:
        """Detect profile spoofing and fake accounts"""
        # Implementation for profile spoofing detection
        return []
    
    async def _detect_activity_anomalies(self, behavioral_analysis: Dict[str, Any]) -> List[DeceptionIndicator]:
        """Detect anomalous activity patterns"""
        # Implementation for activity anomaly detection
        return []
    
    async def _detect_hardware_spoofing(self, digital_footprint: DigitalFootprint) -> List[DeceptionIndicator]:
        """Detect hardware and browser spoofing"""
        # Implementation for hardware spoofing detection
        return []
    
    async def _detect_behavioral_inconsistencies(self, profiles: List[ProfileData],
                                               behavioral_analysis: Dict[str, Any]) -> List[DeceptionIndicator]:
        """Detect behavioral inconsistencies across platforms"""
        # Implementation for behavioral inconsistency detection
        return []
    
    # Utility Methods
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not text:
            return 0
        entropy = 0
        for x in range(256):
  
