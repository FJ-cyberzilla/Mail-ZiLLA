# tests/test_linkedin_agent.py
import pytest
from unittest.mock import AsyncMock, patch
from agents.linkedin_agent import LinkedInAgent

@pytest.mark.asyncio
class TestLinkedInAgent:
    async def test_search_by_email_success(self):
        agent = LinkedInAgent()
        mock_response = {
            "elements": [
                {
                    "publicProfileUrl": "https://linkedin.com/in/johndoe",
                    "vanityName": "johndoe",
                    "firstName": "John",
                    "lastName": "Doe",
                    "headline": "Software Engineer",
                    "location": {"name": "San Francisco"}
                }
            ]
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value.status = 200
            mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            
            results = await agent.search_by_email("john@example.com")
            
            assert len(results) == 1
            assert results[0].platform.value == "linkedin"
            assert results[0].full_name == "John Doe"

    async def test_search_by_email_rate_limit(self):
        agent = LinkedInAgent()
        
        with patch('agents.linkedin_agent.RateLimiter.acquire') as mock_acquire:
            mock_acquire.side_effect = Exception("Rate limit exceeded")
            
            results = await agent.search_by_email("test@example.com")
            assert results == []
