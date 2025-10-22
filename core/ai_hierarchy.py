# In core/ai_hierarchy.py - Add to __init__ method

async def initialize_default_agents(self):
    """Initialize the core platform agents"""
    from agents.linkedin_agent import LinkedInAgent
    from agents.github_agent import GitHubAgent
    from agents.twitter_agent import TwitterAgent
    from agents.facebook_agent import FacebookAgent
    from agents.instagram_agent import InstagramAgent
    
    # Register core agents
    self.register_agent(
        agent_id="linkedin_enterprise",
        agent_instance=LinkedInAgent(),
        role=AIAgentRole.COLLECTOR,
        capabilities=['email_search', 'profile_extraction', 'professional_analysis'],
        weight=0.9
    )
    
    self.register_agent(
        agent_id="github_enterprise", 
        agent_instance=GitHubAgent(),
        role=AIAgentRole.COLLECTOR,
        capabilities=['email_search', 'code_analysis', 'activity_tracking'],
        weight=0.8
    )
    
    self.register_agent(
        agent_id="twitter_enterprise",
        agent_instance=TwitterAgent(), 
        role=AIAgentRole.COLLECTOR,
        capabilities=['email_search', 'phone_search', 'social_analysis'],
        weight=0.7
    )
    
    # Add similar registrations for Facebook and Instagram
    # (These would be implemented next)
