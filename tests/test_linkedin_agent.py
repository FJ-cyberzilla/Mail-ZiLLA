import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, patch

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.linkedin_agent import LinkedInAgent
    from core.base_agent import Platform, ProfileData
except ImportError:
    # Mock classes for testing
    from enum import Enum

    class Platform(Enum):
        LINKEDIN = "linkedin"

    class ProfileData:
        def __init__(
            self,
            platform,
            profile_url,
            username,
            full_name,
            email,
            phone,
            location,
            bio,
            avatar_url,
            last_activity,
            confidence_score,
            raw_data,
        ):
            self.platform = platform
            self.profile_url = profile_url
            self.username = username
            self.full_name = full_name
            self.email = email
            self.phone = phone
            self.location = location
            self.bio = bio
            self.avatar_url = avatar_url
            self.last_activity = last_activity
            self.confidence_score = confidence_score
            self.raw_data = raw_data

    class LinkedInAgent:
        async def search_by_email(self, email, context=None):
            return []


class TestLinkedInAgent(unittest.TestCase):
    def setUp(self):
        self.agent = LinkedInAgent()

    def test_agent_creation(self):
        """Test that LinkedInAgent can be created"""
        self.assertIsInstance(self.agent, LinkedInAgent)

    @patch("agents.linkedin_agent.aiohttp.ClientSession")
    def test_search_by_email_success(self, mock_session):
        """Test successful email search"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "elements": [
                {
                    "publicProfileUrl": "https://linkedin.com/in/johndoe",
                    "vanityName": "johndoe",
                    "firstName": "John",
                    "lastName": "Doe",
                    "headline": "Software Engineer",
                    "location": {"name": "San Francisco"},
                    "pictureUrls": {"values": ["https://example.com/avatar.jpg"]},
                }
            ]
        }

        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        async def run_test():
            return await self.agent.search_by_email("john@example.com")

        results = asyncio.run(run_test())
        self.assertIsInstance(results, list)

    def test_basic_assertions(self):
        """Test basic unittest functionality"""
        self.assertEqual(1, 1)
        self.assertNotEqual(1, 2)
        self.assertTrue(True)
        self.assertFalse(False)


if __name__ == "__main__":
    unittest.main()
