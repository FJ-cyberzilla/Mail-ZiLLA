# tests/test_social_agent.py
import pytest
from core.social_agent import social_agent

class TestSocialAgent:
    @pytest.mark.asyncio
    async def test_email_lookup_basic(self):
        result = await social_agent.process_email("test@example.com")
        assert result.confidence_score >= 0.0
        assert result.confidence_score <= 1.0
    
    @pytest.mark.asyncio 
    async def test_phone_lookup(self):
        result = await social_agent.process_phone("+1234567890")
        assert isinstance(result.profiles, list)

# tests/test_validation.py
# tests/test_database.py  
# tests/test_api.py
# tests/test_security.py
