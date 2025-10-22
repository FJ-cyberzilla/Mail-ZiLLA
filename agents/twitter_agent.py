"""
TWITTER AGENT - Social Media Intelligence
Twitter profile discovery and social activity analysis
"""

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.base_agent import BaseSocialAgent
from core.schemas import PlatformType, ProfileData


class TwitterAgent(BaseSocialAgent):
    """
    Twitter Intelligence Agent
    Social media profile discovery and activity analysis
    """

    def __init__(self):
        super().__init__(PlatformType.TWITTER, "twitter_enterprise_agent")
        self.logger = logging.getLogger("agent.twitter")

        # Twitter-specific configuration
        self.include_tweets = False  # Due to API limitations
        self.analyze_engagement = True
        self.extract_following = False

        # API credentials (would be from environment)
        self.bearer_token = None

    async def search_by_email(
        self, email: str, context: Dict[str, Any] = None
    ) -> List[ProfileData]:
        """
        Search Twitter profiles by email address
        Uses Twitter API v2 for user lookup
        """
        self.logger.info(f"🔍 Searching Twitter for email: {email}")

        profiles = []

        try:
            # Twitter API v2 user lookup by email
            users_url = f"{self.platform_config['base_url']}/2/users/by"
            params = {
                "user.fields": "created_at,description,location,name,profile_image_url,public_metrics,url,username,verified",
                "email": email,
            }

            headers = {}
            if self.bearer_token:
                headers["Authorization"] = f"Bearer {self.bearer_token}"

            success, response = await self._make_request(
                "GET", users_url, params=params, headers=headers
            )
            if success:
                data = json.loads(response)
                profiles.extend(self._parse_twitter_users(data, email))

        except Exception as e:
            self.logger.warning(f"Twitter email search failed: {e}")

        # Try alternative strategies if primary fails
        if not profiles:
            try:
                # Search by name derived from email
                name_from_email = email.split("@")[0].replace(".", " ").title()
                name_profiles = await self._search_by_name(name_from_email, email)
                profiles.extend(name_profiles)
            except Exception as e:
                self.logger.debug(f"Twitter name search failed: {e}")

        self.logger.info(f"📊 Twitter search completed: {len(profiles)} profiles found")
        return profiles

    async def search_by_phone(
        self, phone: str, context: Dict[str, Any] = None
    ) -> List[ProfileData]:
        """
        Search Twitter profiles by phone number
        Twitter API supports phone number lookup
        """
        self.logger.info(f"📱 Searching Twitter for phone: {phone}")

        profiles = []

        try:
            # Twitter API v2 user lookup by phone
            users_url = f"{self.platform_config['base_url']}/2/users/by"
            params = {
                "user.fields": "created_at,description,location,name,profile_image_url,public_metrics,url,username,verified",
                "phone": phone,
            }

            headers = {}
            if self.bearer_token:
                headers["Authorization"] = f"Bearer {self.bearer_token}"

            success, response = await self._make_request(
                "GET", users_url, params=params, headers=headers
            )
            if success:
                data = json.loads(response)
                profiles.extend(self._parse_twitter_users(data, phone))

        except Exception as e:
            self.logger.warning(f"Twitter phone search failed: {e}")

        return profiles

    async def _search_by_name(
        self, name: str, original_email: str
    ) -> List[ProfileData]:
        """Search Twitter users by name"""
        profiles = []

        try:
            # Twitter user search by name/username
            search_url = f"{self.platform_config['base_url']}/2/users/search"
            params = {
                "query": name,
                "user.fields": "created_at,description,location,name,profile_image_url,public_metrics,url,username,verified",
                "max_results": 10,
            }

            headers = {}
            if self.bearer_token:
                headers["Authorization"] = f"Bearer {self.bearer_token}"

            success, response = await self._make_request(
                "GET", search_url, params=params, headers=headers
            )
            if success:
                data = json.loads(response)

                for user_data in data.get("data", []):
                    profile = self._parse_twitter_user(user_data, original_email)
                    if profile:
                        profiles.append(profile)

        except Exception as e:
            self.logger.debug(f"Twitter name search failed: {e}")

        return profiles

    def _parse_twitter_users(
        self, response_data: Dict, identifier: str
    ) -> List[ProfileData]:
        """Parse Twitter API users response"""
        profiles = []

        try:
            for user_data in response_data.get("data", []):
                profile = self._parse_twitter_user(user_data, identifier)
                if profile:
                    profiles.append(profile)

        except Exception as e:
            self.logger.warning(f"Failed to parse Twitter users: {e}")

        return profiles

    def _parse_twitter_user(
        self, user_data: Dict, identifier: str
    ) -> Optional[ProfileData]:
        """Parse individual Twitter user data"""
        try:
            # Basic profile information
            profile = ProfileData(
                platform=PlatformType.TWITTER,
                profile_url=f"https://twitter.com/{user_data.get('username')}",
                username=user_data.get("username"),
                full_name=user_data.get("name"),
                email=identifier if "@" in identifier else None,
                location=user_data.get("location"),
                company=self._extract_company_from_bio(
                    user_data.get("description", "")
                ),
                job_title=None,  # Twitter doesn't have job titles
                profile_picture=user_data.get("profile_image_url"),
                last_activity=self._parse_twitter_activity(user_data),
                bio=user_data.get("description"),
                confidence=self._calculate_twitter_confidence(user_data),
                is_verified=user_data.get("verified", False),
                raw_data=user_data,
            )

            return profile

        except Exception as e:
            self.logger.debug(f"Failed to parse Twitter user: {e}")
            return None

    def _extract_company_from_bio(self, bio: str) -> Optional[str]:
        """Extract company information from Twitter bio"""
        if not bio:
            return None

        # Common patterns for company mentions
        company_patterns = [
            r"@([A-Za-z0-9_]+)",  # @company handles
            r"at\s+([A-Z][A-Za-z0-9\s&]+)(?=\s|$)",  # "at Company"
            r"@\s+([A-Z][A-Za-z0-9\s&]+)(?=\s|$)",  # "@ Company"
        ]

        for pattern in company_patterns:
            matches = re.findall(pattern, bio, re.IGNORECASE)
            if matches:
                return matches[0].strip()

        return None

    def _parse_twitter_activity(self, user_data: Dict) -> Optional[datetime]:
        """Parse last activity from Twitter profile"""
        try:
            # Twitter provides account creation date
            created_at = user_data.get("created_at")
            if created_at:
                return datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except:
            pass

        return None

    def _calculate_twitter_confidence(self, user_data: Dict) -> float:
        """Calculate confidence score for Twitter profile"""
        confidence_factors = []

        # Account verification
        if user_data.get("verified"):
            confidence_factors.append(0.9)

        # Follower count
        metrics = user_data.get("public_metrics", {})
        followers = metrics.get("followers_count", 0)
        if followers > 1000:
            confidence_factors.append(0.8)
        elif followers > 100:
            confidence_factors.append(0.6)
        elif followers > 10:
            confidence_factors.append(0.4)

        # Tweet count
        tweet_count = metrics.get("tweet_count", 0)
        if tweet_count > 1000:
            confidence_factors.append(0.7)
        elif tweet_count > 100:
            confidence_factors.append(0.5)
        elif tweet_count > 10:
            confidence_factors.append(0.3)

        # Profile completeness
        filled_fields = sum(
            1
            for field in [
                user_data.get("description"),
                user_data.get("location"),
                user_data.get("url"),
            ]
            if field
        )

        completeness_score = filled_fields / 3
        confidence_factors.append(completeness_score * 0.6)

        # Account age
        created_at = user_data.get("created_at")
        if created_at:
            try:
                account_age = (
                    datetime.now()
                    - datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                ).days
                if account_age > 365:
                    confidence_factors.append(0.7)
                elif account_age > 180:
                    confidence_factors.append(0.5)
            except:
                pass

        return (
            sum(confidence_factors) / len(confidence_factors)
            if confidence_factors
            else 0.3
        )

    async def search_by_username(
        self, username: str, context: Dict[str, Any] = None
    ) -> List[ProfileData]:
        """
        Search Twitter profile by username
        """
        try:
            users_url = (
                f"{self.platform_config['base_url']}/2/users/by/username/{username}"
            )
            params = {
                "user.fields": "created_at,description,location,name,profile_image_url,public_metrics,url,username,verified"
            }

            headers = {}
            if self.bearer_token:
                headers["Authorization"] = f"Bearer {self.bearer_token}"

            success, response = await self._make_request(
                "GET", users_url, params=params, headers=headers
            )
            if success:
                data = json.loads(response)
                user_data = data.get("data")
                if user_data:
                    profile = self._parse_twitter_user(user_data, username)
                    return [profile] if profile else []

        except Exception as e:
            self.logger.warning(f"Twitter username search failed: {e}")

        return []


# Agent instance for easy import
twitter_agent = TwitterAgent()
