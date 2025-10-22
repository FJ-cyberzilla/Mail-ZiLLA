"""
GITHUB AGENT - Code Platform Intelligence
GitHub profile discovery and developer activity analysis
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.base_agent import BaseCodeAgent
from core.schemas import PlatformType, ProfileData


class GitHubAgent(BaseCodeAgent):
    """
    GitHub Intelligence Agent
    Developer profile discovery and code activity analysis
    """

    def __init__(self):
        super().__init__(PlatformType.GITHUB, "github_enterprise_agent")
        self.logger = logging.getLogger("agent.github")

        # GitHub-specific configuration
        self.include_repositories = True
        self.analyze_activity = True
        self.extract_contributions = True

        # API token (would be from environment in production)
        self.api_token = None

    async def search_by_email(
        self, email: str, context: Dict[str, Any] = None
    ) -> List[ProfileData]:
        """
        Search GitHub profiles by email address
        Uses GitHub's powerful email search capabilities
        """
        self.logger.info(f"🔍 Searching GitHub for email: {email}")

        profiles = []
        strategies = [
            self._search_github_api,
            self._search_github_commits,
            self._search_github_organizations,
        ]

        for strategy in strategies:
            try:
                strategy_profiles = await strategy(email, context)
                profiles.extend(strategy_profiles)

                # GitHub email search is usually very accurate
                if strategy_profiles:
                    self.logger.info(
                        f"✅ Found {len(strategy_profiles)} GitHub profiles"
                    )
                    break

            except Exception as e:
                self.logger.warning(f"GitHub search strategy failed: {e}")
                continue

        # Enrich profiles with additional data
        enriched_profiles = []
        for profile in profiles:
            try:
                enriched_profile = await self._enrich_github_profile(profile)
                enriched_profiles.append(enriched_profile)
            except Exception as e:
                self.logger.debug(f"Failed to enrich GitHub profile: {e}")
                enriched_profiles.append(profile)

        self.logger.info(
            f"📊 GitHub search completed: {len(enriched_profiles)} profiles found"
        )
        return enriched_profiles

    async def search_by_phone(
        self, phone: str, context: Dict[str, Any] = None
    ) -> List[ProfileData]:
        """
        Search GitHub profiles by phone number
        GitHub doesn't support phone search directly, but we can try alternatives
        """
        self.logger.info(f"📱 Searching GitHub for phone: {phone}")

        # GitHub doesn't support phone search natively
        # We can try searching for phone in commit messages or user bios
        profiles = []

        try:
            # Search users with potential phone references
            search_url = f"{self.platform_config['base_url']}/search/users"
            params = {
                "q": f"{phone} in:email",  # Try to find phone in email fields
                "per_page": 10,
            }

            success, response = await self._make_request(
                "GET", search_url, params=params
            )
            if success:
                data = json.loads(response)
                for user_data in data.get("items", []):
                    profile = await self._get_user_profile(user_data["login"])
                    if profile:
                        profiles.append(profile)

        except Exception as e:
            self.logger.debug(f"GitHub phone search failed: {e}")

        return profiles

    async def _search_github_api(
        self, email: str, context: Dict[str, Any]
    ) -> List[ProfileData]:
        """Search GitHub users by email via API"""
        profiles = []

        try:
            # GitHub user search by email
            search_url = f"{self.platform_config['base_url']}/search/users"
            params = {"q": f"{email} in:email", "per_page": 20}

            # Add authentication if available
            headers = {}
            if self.api_token:
                headers["Authorization"] = f"token {self.api_token}"

            success, response = await self._make_request(
                "GET", search_url, params=params, headers=headers
            )
            if success:
                data = json.loads(response)

                for user_data in data.get("items", []):
                    profile = await self._get_user_profile(user_data["login"])
                    if profile:
                        profiles.append(profile)

        except Exception as e:
            self.logger.debug(f"GitHub API search failed: {e}")

        return profiles

    async def _search_github_commits(
        self, email: str, context: Dict[str, Any]
    ) -> List[ProfileData]:
        """Search GitHub commits by email to find contributors"""
        profiles = []

        try:
            # Search commits by author email
            search_url = f"{self.platform_config['base_url']}/search/commits"
            params = {"q": f"author-email:{email}", "per_page": 10}

            headers = {"Accept": "application/vnd.github.cloak-preview"}
            if self.api_token:
                headers["Authorization"] = f"token {self.api_token}"

            success, response = await self._make_request(
                "GET", search_url, params=params, headers=headers
            )
            if success:
                data = json.loads(response)

                for commit_data in data.get("items", []):
                    author = commit_data.get("author")
                    if author:
                        profile = await self._get_user_profile(author["login"])
                        if profile and profile not in profiles:
                            profiles.append(profile)

        except Exception as e:
            self.logger.debug(f"GitHub commit search failed: {e}")

        return profiles

    async def _search_github_organizations(
        self, email: str, context: Dict[str, Any]
    ) -> List[ProfileData]:
        """Search through organization memberships"""
        profiles = []

        try:
            # This would require additional context about organizations
            # For now, return empty - could be enhanced with organization context
            pass

        except Exception as e:
            self.logger.debug(f"GitHub organization search failed: {e}")

        return profiles

    async def _get_user_profile(self, username: str) -> Optional[ProfileData]:
        """Get detailed user profile from GitHub"""
        try:
            user_url = f"{self.platform_config['base_url']}/users/{username}"

            headers = {}
            if self.api_token:
                headers["Authorization"] = f"token {self.api_token}"

            success, response = await self._make_request(
                "GET", user_url, headers=headers
            )
            if not success:
                return None

            user_data = json.loads(response)
            return self._parse_github_profile(user_data)

        except Exception as e:
            self.logger.debug(f"Failed to get GitHub user profile: {e}")
            return None

    def _parse_github_profile(self, user_data: Dict) -> ProfileData:
        """Parse GitHub user data into ProfileData"""
        try:
            # Basic profile information
            profile = ProfileData(
                platform=PlatformType.GITHUB,
                profile_url=user_data.get("html_url"),
                username=user_data.get("login"),
                full_name=user_data.get("name"),
                email=user_data.get("email"),
                location=user_data.get("location"),
                company=user_data.get("company"),
                job_title=None,  # GitHub doesn't have job titles
                profile_picture=user_data.get("avatar_url"),
                last_activity=self._parse_github_activity(user_data),
                bio=user_data.get("bio"),
                confidence=self._calculate_github_confidence(user_data),
                is_verified=user_data.get("is_verified", False),
                raw_data=user_data,
            )

            return profile

        except Exception as e:
            self.logger.error(f"Failed to parse GitHub profile: {e}")
            raise

    def _parse_github_activity(self, user_data: Dict) -> Optional[datetime]:
        """Parse last activity from GitHub profile"""
        try:
            # GitHub provides updated_at for profile activity
            updated_at = user_data.get("updated_at")
            if updated_at:
                return datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        except:
            pass

        return None

    def _calculate_github_confidence(self, user_data: Dict) -> float:
        """Calculate confidence score for GitHub profile"""
        confidence_factors = []

        # Account age (older accounts are more legitimate)
        created_at = user_data.get("created_at")
        if created_at:
            try:
                account_age = (
                    datetime.now()
                    - datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                ).days
                if account_age > 365:
                    confidence_factors.append(0.9)
                elif account_age > 180:
                    confidence_factors.append(0.7)
                elif account_age > 30:
                    confidence_factors.append(0.5)
            except:
                pass

        # Followers count
        followers = user_data.get("followers", 0)
        if followers > 100:
            confidence_factors.append(0.8)
        elif followers > 10:
            confidence_factors.append(0.6)
        elif followers > 0:
            confidence_factors.append(0.4)

        # Public repositories
        public_repos = user_data.get("public_repos", 0)
        if public_repos > 10:
            confidence_factors.append(0.7)
        elif public_repos > 0:
            confidence_factors.append(0.5)

        # Profile completeness
        filled_fields = sum(
            1
            for field in [
                user_data.get("name"),
                user_data.get("bio"),
                user_data.get("location"),
                user_data.get("company"),
            ]
            if field
        )

        completeness_score = filled_fields / 4
        confidence_factors.append(completeness_score * 0.6)

        return (
            sum(confidence_factors) / len(confidence_factors)
            if confidence_factors
            else 0.3
        )

    async def _enrich_github_profile(self, profile: ProfileData) -> ProfileData:
        """Enrich GitHub profile with additional data"""
        try:
            if self.include_repositories:
                repositories = await self.get_repositories(profile.username)
                profile.raw_data["repositories"] = repositories

            if self.analyze_activity:
                activity = await self.analyze_activity(profile.username)
                profile.raw_data["activity_analysis"] = activity

            if self.extract_contributions:
                contributions = await self.get_contribution_graph(profile.username)
                profile.raw_data["contributions"] = contributions

        except Exception as e:
            self.logger.debug(f"Failed to enrich GitHub profile: {e}")

        return profile

    async def get_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Get user repositories with activity data"""
        try:
            repos_url = f"{self.platform_config['base_url']}/users/{username}/repos"
            params = {"sort": "updated", "per_page": 20}

            headers = {}
            if self.api_token:
                headers["Authorization"] = f"token {self.api_token}"

            success, response = await self._make_request(
                "GET", repos_url, params=params, headers=headers
            )
            if success:
                repos_data = json.loads(response)

                repositories = []
                for repo in repos_data:
                    repositories.append(
                        {
                            "name": repo.get("name"),
                            "full_name": repo.get("full_name"),
                            "description": repo.get("description"),
                            "language": repo.get("language"),
                            "stars": repo.get("stargazers_count"),
                            "forks": repo.get("forks_count"),
                            "updated_at": repo.get("updated_at"),
                            "is_fork": repo.get("fork", False),
                        }
                    )

                return repositories

        except Exception as e:
            self.logger.debug(f"Failed to get repositories: {e}")

        return []

    async def analyze_activity(self, username: str) -> Dict[str, Any]:
        """Analyze user activity patterns"""
        try:
            events_url = f"{self.platform_config['base_url']}/users/{username}/events"

            headers = {}
            if self.api_token:
                headers["Authorization"] = f"token {self.api_token}"

            success, response = await self._make_request(
                "GET", events_url, headers=headers
            )
            if success:
                events_data = json.loads(response)

                # Analyze event types and frequency
                event_counts = {}
                for event in events_data:
                    event_type = event.get("type")
                    event_counts[event_type] = event_counts.get(event_type, 0) + 1

                return {
                    "total_events": len(events_data),
                    "event_breakdown": event_counts,
                    "recent_activity": len(events_data) > 0,
                    "primary_activity": (
                        max(event_counts, key=event_counts.get)
                        if event_counts
                        else None
                    ),
                }

        except Exception as e:
            self.logger.debug(f"Failed to analyze activity: {e}")

        return {
            "total_events": 0,
            "event_breakdown": {},
            "recent_activity": False,
            "primary_activity": None,
        }

    async def get_contribution_graph(self, username: str) -> Dict[str, Any]:
        """Get contribution activity graph (simplified)"""
        try:
            # Note: GitHub's contribution graph isn't directly available via API
            # This is a simplified implementation
            user_url = f"{self.platform_config['base_url']}/users/{username}"

            headers = {}
            if self.api_token:
                headers["Authorization"] = f"token {self.api_token}"

            success, response = await self._make_request(
                "GET", user_url, headers=headers
            )
            if success:
                user_data = json.loads(response)

                return {
                    "public_repos": user_data.get("public_repos", 0),
                    "public_gists": user_data.get("public_gists", 0),
                    "followers": user_data.get("followers", 0),
                    "following": user_data.get("following", 0),
                    "account_age_days": self._calculate_account_age(
                        user_data.get("created_at")
                    ),
                }

        except Exception as e:
            self.logger.debug(f"Failed to get contribution graph: {e}")

        return {}

    def _calculate_account_age(self, created_at: str) -> int:
        """Calculate account age in days"""
        try:
            if created_at:
                created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                return (datetime.now() - created_date).days
        except:
            pass
        return 0


# Agent instance for easy import
github_agent = GitHubAgent()
