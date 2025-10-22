"""
LINKEDIN AGENT - Professional Network Intelligence
Enterprise-grade LinkedIn profile discovery and analysis
"""

import re
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from core.base_agent import BaseSocialAgent
from core.schemas import ProfileData, PlatformType

class LinkedInAgent(BaseSocialAgent):
    """
    LinkedIn Intelligence Agent
    Professional network profile discovery and correlation
    """
    
    def __init__(self):
        super().__init__(PlatformType.LINKEDIN, "linkedin_enterprise_agent")
        self.logger = logging.getLogger("agent.linkedin")
        
        # LinkedIn-specific configuration
        self.search_depth = "deep"  # deep, standard, basic
        self.include_connections = False
        self.extract_companies = True
        
    async def search_by_email(self, email: str, context: Dict[str, Any] = None) -> List[ProfileData]:
        """
        Search LinkedIn profiles by email address
        Uses multiple strategies for comprehensive coverage
        """
        self.logger.info(f"🔍 Searching LinkedIn for email: {email}")
        
        profiles = []
        strategies = [
            self._search_linkedin_direct,
            self._search_linkedin_advanced,
            self._search_linkedin_sales_navigator
        ]
        
        for strategy in strategies:
            try:
                strategy_profiles = await strategy(email, context)
                profiles.extend(strategy_profiles)
                
                # If we found good matches, we can stop
                high_confidence_profiles = [p for p in strategy_profiles if p.confidence > 0.7]
                if high_confidence_profiles:
                    self.logger.info(f"✅ Found {len(high_confidence_profiles)} high-confidence LinkedIn profiles")
                    break
                    
            except Exception as e:
                self.logger.warning(f"LinkedIn search strategy failed: {e}")
                continue
        
        # Deduplicate profiles
        unique_profiles = self._deduplicate_profiles(profiles)
        self.logger.info(f"📊 LinkedIn search completed: {len(unique_profiles)} unique profiles found")
        
        return unique_profiles
    
    async def search_by_phone(self, phone: str, context: Dict[str, Any] = None) -> List[ProfileData]:
        """
        Search LinkedIn profiles by phone number
        LinkedIn has limited phone search capabilities
        """
        self.logger.info(f"📱 Searching LinkedIn for phone: {phone}")
        
        # LinkedIn primarily uses email, but we can try some strategies
        profiles = []
        
        try:
            # Strategy 1: Try phone in search queries
            search_url = f"{self.platform_config['base_url']}/voyager/api/search/hits"
            params = {
                'keywords': phone,
                'filters': 'List()',
                'q': 'all',
                'start': 0,
                'count': 10
            }
            
            success, response = await self._make_request('GET', search_url, params=params)
            if success:
                profiles.extend(self._parse_linkedin_search_results(response, phone))
                
        except Exception as e:
            self.logger.warning(f"LinkedIn phone search failed: {e}")
        
        return profiles
    
    async def _search_linkedin_direct(self, email: str, context: Dict[str, Any]) -> List[ProfileData]:
        """Direct LinkedIn search using email"""
        profiles = []
        
        try:
            # Strategy 1: Direct profile search
            search_url = f"{self.platform_config['base_url']}/sales-api/salesApiProfiles"
            payload = {
                'query': {
                    'emailAddress': email,
                    'searchScope': 'ALL'
                },
                'start': 0,
                'count': 25
            }
            
            success, response = await self._make_request('POST', search_url, json=payload)
            if success:
                profiles.extend(self._parse_linkedin_api_response(response, email))
                
        except Exception as e:
            self.logger.debug(f"LinkedIn direct search failed: {e}")
        
        return profiles
    
    async def _search_linkedin_advanced(self, email: str, context: Dict[str, Any]) -> List[ProfileData]:
        """Advanced LinkedIn search using multiple parameters"""
        profiles = []
        
        try:
            # Extract name from email for better search
            name_from_email = email.split('@')[0].replace('.', ' ').title()
            
            # Advanced search URL
            search_url = f"{self.platform_config['base_url']}/voyager/api/search/cluster"
            params = {
                'keywords': f"{name_from_email} {email}",
                'origin': 'SWITCH_SEARCH_VERTICAL',
                'q': 'all',
                'filters': 'List((resultType,List(PEOPLE)))',
                'start': 0,
                'count': 20
            }
            
            success, response = await self._make_request('GET', search_url, params=params)
            if success:
                profiles.extend(self._parse_linkedin_advanced_results(response, email))
                
        except Exception as e:
            self.logger.debug(f"LinkedIn advanced search failed: {e}")
        
        return profiles
    
    async def _search_linkedin_sales_navigator(self, email: str, context: Dict[str, Any]) -> List[ProfileData]:
        """Sales Navigator search (if available)"""
        profiles = []
        
        try:
            # Sales Navigator API endpoint
            nav_url = f"{self.platform_config['base_url']}/sales-api/salesApiEngagements"
            payload = {
                'filters': {
                    'emailAddress': email
                },
                'start': 0,
                'count': 10
            }
            
            success, response = await self._make_request('POST', nav_url, json=payload)
            if success:
                profiles.extend(self._parse_sales_navigator_response(response, email))
                
        except Exception as e:
            self.logger.debug(f"Sales Navigator search failed: {e}")
        
        return profiles
    
    def _parse_linkedin_api_response(self, response_data: str, original_email: str) -> List[ProfileData]:
        """Parse LinkedIn API response"""
        profiles = []
        
        try:
            data = json.loads(response_data)
            
            for element in data.get('elements', []):
                profile = self._extract_profile_from_element(element, original_email)
                if profile:
                    profiles.append(profile)
                    
        except Exception as e:
            self.logger.warning(f"Failed to parse LinkedIn API response: {e}")
        
        return profiles
    
    def _parse_linkedin_advanced_results(self, response_data: str, original_email: str) -> List[ProfileData]:
        """Parse advanced LinkedIn search results"""
        profiles = []
        
        try:
            data = json.loads(response_data)
            
            for cluster in data.get('elements', []):
                for item in cluster.get('items', []):
                    profile = self._extract_profile_from_search_item(item, original_email)
                    if profile:
                        profiles.append(profile)
                        
        except Exception as e:
            self.logger.warning(f"Failed to parse LinkedIn advanced results: {e}")
        
        return profiles
    
    def _parse_sales_navigator_response(self, response_data: str, original_email: str) -> List[ProfileData]:
        """Parse Sales Navigator response"""
        profiles = []
        
        try:
            data = json.loads(response_data)
            
            for profile_data in data.get('elements', []):
                profile = self._extract_profile_from_navigator(profile_data, original_email)
                if profile:
                    profiles.append(profile)
                    
        except Exception as e:
            self.logger.warning(f"Failed to parse Sales Navigator response: {e}")
        
        return profiles
    
    def _extract_profile_from_element(self, element: Dict, original_email: str) -> Optional[ProfileData]:
        """Extract profile data from LinkedIn API element"""
        try:
            profile_info = element.get('profile', {})
            contact_info = element.get('contactInfo', {})
            
            # Basic profile data
            full_name = f"{profile_info.get('firstName', '')} {profile_info.get('lastName', '')}".strip()
            if not full_name:
                return None
            
            # Build profile URL
            profile_id = profile_info.get('id')
            profile_url = f"https://www.linkedin.com/in/{profile_info.get('vanityName', profile_id)}" if profile_id else None
            
            # Extract company information
            company_info = self._extract_company_info(profile_info)
            
            # Create profile
            profile = ProfileData(
                platform=PlatformType.LINKEDIN,
                profile_url=profile_url,
                username=profile_info.get('vanityName'),
                full_name=full_name,
                email=original_email,  # Use searched email
                location=profile_info.get('locationName'),
                company=company_info.get('company'),
                job_title=company_info.get('title'),
                profile_picture=profile_info.get('pictureInfo', {}).get('rootUrl'),
                last_activity=self._parse_last_activity(profile_info),
                bio=self._extract_bio(profile_info),
                confidence=self._calculate_linkedin_confidence(profile_info, original_email),
                is_verified=True,  # LinkedIn profiles are generally verified
                raw_data=element
            )
            
            return await self.enrich_profile_data(profile)
            
        except Exception as e:
            self.logger.debug(f"Failed to extract profile from element: {e}")
            return None
    
    def _extract_company_info(self, profile_info: Dict) -> Dict[str, str]:
        """Extract company and job title information"""
        company_info = {}
        
        try:
            # Current position
            positions = profile_info.get('positions', {}).get('values', [])
            current_position = next((p for p in positions if p.get('isCurrent', False)), None)
            
            if current_position:
                company_info['company'] = current_position.get('company', {}).get('name')
                company_info['title'] = current_position.get('title')
                
        except Exception as e:
            self.logger.debug(f"Failed to extract company info: {e}")
        
        return company_info
    
    def _parse_last_activity(self, profile_info: Dict) -> Optional[datetime]:
        """Parse last activity timestamp"""
        try:
            # LinkedIn provides various activity indicators
            activity_timestamps = []
            
            # Last post activity
            if 'activityTimestamps' in profile_info:
                activity_timestamps.extend(profile_info['activityTimestamps'])
            
            # Profile update timestamp
            if 'lastModified' in profile_info:
                activity_timestamps.append(profile_info['lastModified'])
            
            if activity_timestamps:
                latest_timestamp = max(activity_timestamps)
                return datetime.fromtimestamp(latest_timestamp / 1000)
                
        except Exception:
            pass
        
        return None
    
    def _extract_bio(self, profile_info: Dict) -> str:
        """Extract bio/summary from profile"""
        try:
            return profile_info.get('summary', '')
        except:
            return ''
    
    def _calculate_linkedin_confidence(self, profile_info: Dict, original_email: str) -> float:
        """Calculate confidence score for LinkedIn profile match"""
        confidence_factors = []
        
        # Name consistency
        if profile_info.get('firstName') and profile_info.get('lastName'):
            confidence_factors.append(0.8)
        
        # Profile completeness
        filled_fields = sum(1 for field in [
            profile_info.get('headline'),
            profile_info.get('industry'),
            profile_info.get('locationName'),
            profile_info.get('positions')
        ] if field)
        
        completeness_score = filled_fields / 4
        confidence_factors.append(completeness_score * 0.7)
        
        # Connection count (more connections = higher confidence)
        connection_count = profile_info.get('connections', 0)
        if connection_count > 500:
            confidence_factors.append(0.9)
        elif connection_count > 100:
            confidence_factors.append(0.7)
        elif connection_count > 10:
            confidence_factors.append(0.5)
        
        # Profile picture
        if profile_info.get('pictureInfo', {}).get('rootUrl'):
            confidence_factors.append(0.6)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.3
    
    def _deduplicate_profiles(self, profiles: List[ProfileData]) -> List[ProfileData]:
        """Remove duplicate profiles based on profile URL and name"""
        seen_urls = set()
        unique_profiles = []
        
        for profile in profiles:
            if profile.profile_url and profile.profile_url not in seen_urls:
                seen_urls.add(profile.profile_url)
                unique_profiles.append(profile)
            elif not profile.profile_url and profile.full_name:
                # Use name-based deduplication for profiles without URLs
                name_key = profile.full_name.lower()
                if name_key not in seen_urls:
                    seen_urls.add(name_key)
                    unique_profiles.append(profile)
        
        return unique_profiles
    
    async def extract_profile_data(self, profile_url: str) -> ProfileData:
        """
        Extract detailed profile data from LinkedIn URL
        """
        self.logger.info(f"📄 Extracting LinkedIn profile data from: {profile_url}")
        
        try:
            # Extract profile ID from URL
            profile_match = re.search(r'/in/([^/?]+)', profile_url)
            if not profile_match:
                raise ValueError("Invalid LinkedIn profile URL")
            
            profile_id = profile_match.group(1)
            
            # Fetch profile data
            profile_api_url = f"{self.platform_config['base_url']}/voyager/api/identity/profiles/{profile_id}/profileView"
            
            success, response = await self._make_request('GET', profile_api_url)
            if not success:
                raise Exception(f"Failed to fetch profile: {response}")
            
            # Parse profile data
            profile_data = json.loads(response)
            return self._parse_detailed_profile(profile_data, profile_url)
            
        except Exception as e:
            self.logger.error(f"Failed to extract LinkedIn profile data: {e}")
            raise
    
    def _parse_detailed_profile(self, profile_data: Dict, profile_url: str) -> ProfileData:
        """Parse detailed LinkedIn profile data"""
        try:
            profile_info = profile_data.get('profile', {})
            
            full_name = f"{profile_info.get('firstName', '')} {profile_info.get('lastName', '')}".strip()
            
            return ProfileData(
                platform=PlatformType.LINKEDIN,
                profile_url=profile_url,
                username=profile_info.get('vanityName'),
                full_name=full_name,
                email=None,  # Email not available in public profile
                location=profile_info.get('locationName'),
                company=self._extract_current_company(profile_info),
                job_title=self._extract_current_title(profile_info),
                profile_picture=profile_info.get('pictureInfo', {}).get('rootUrl'),
                last_activity=self._parse_last_activity(profile_info),
                bio=profile_info.get('summary', ''),
                confidence=0.9,  # High confidence for direct profile access
                is_verified=True,
                raw_data=profile_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse detailed LinkedIn profile: {e}")
            raise
    
    def _extract_current_company(self, profile_info: Dict) -> str:
        """Extract current company from profile"""
        try:
            positions = profile_info.get('positions', {}).get('values', [])
            current_position = next((p for p in positions if p.get('isCurrent', False)), None)
            return current_position.get('company', {}).get('name') if current_position else None
        except:
            return None
    
    def _extract_current_title(self, profile_info: Dict) -> str:
        """Extract current job title from profile"""
        try:
            positions = profile_info.get('positions', {}).get('values', [])
            current_position = next((p for p in positions if p.get('isCurrent', False)), None)
            return current_position.get('title') if current_position else None
        except:
            return None

# Agent instance for easy import
linkedin_agent = LinkedInAgent()
