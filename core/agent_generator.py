"""
AI AGENT GENERATOR & ORCHESTRATOR
Dynamically generates, validates, and replaces agents based on performance
"""

import asyncio
import importlib
import inspect
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass
from enum import Enum
import logging
import json
from pathlib import Path
import hashlib

class AgentStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    OFFLINE = "offline"

@dataclass
class AgentPerformance:
    success_rate: float
    avg_response_time: float
    error_rate: float
    last_success: Optional[datetime]
    total_requests: int

@dataclass
class GeneratedAgent:
    agent_id: str
    platform: str
    agent_class: Type
    performance: AgentPerformance
    status: AgentStatus
    config_hash: str

class AgentGenerator:
    """
    Dynamic AI Agent Generation and Management
    Creates and manages agents with automatic replacement for failing instances
    """
    
    def __init__(self):
        self.logger = logging.getLogger("agent_generator")
        self.active_agents: Dict[str, GeneratedAgent] = {}
        self.agent_templates = self._load_agent_templates()
        self.performance_thresholds = {
            'success_rate_min': 0.7,
            'response_time_max': 30.0,
            'error_rate_max': 0.3
        }
        
    def _load_agent_templates(self) -> Dict[str, Any]:
        """Load agent templates for dynamic generation"""
        return {
            'linkedin': {
                'base_class': 'BaseSocialAgent',
                'timeout': 30,
                'rate_limit': 10,
                'required_methods': ['search_by_email', 'search_by_name', 'extract_profile_data'],
                'platform_specific': ['company_extraction', 'job_title_parsing']
            },
            'github': {
                'base_class': 'BaseCodeAgent', 
                'timeout': 20,
                'rate_limit': 30,
                'required_methods': ['search_by_email', 'get_repositories', 'analyze_activity'],
                'platform_specific': ['commit_analysis', 'repository_parsing']
            },
            # ... templates for all platforms
        }
    
    async def generate_agent(self, platform: str, config: Dict[str, Any] = None) -> GeneratedAgent:
        """Dynamically generate an AI agent for a specific platform"""
        self.logger.info(f"🤖 Generating agent for platform: {platform}")
        
        try:
            # Generate unique agent ID
            agent_id = f"{platform}_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}"
            
            # Create agent instance
            agent_class = await self._create_agent_class(platform, config)
            agent_instance = agent_class()
            
            # Initialize with performance tracking
            performance = AgentPerformance(
                success_rate=1.0,  # Start optimistic
                avg_response_time=0.0,
                error_rate=0.0,
                last_success=datetime.now(),
                total_requests=0
            )
            
            generated_agent = GeneratedAgent(
                agent_id=agent_id,
                platform=platform,
                agent_class=agent_class,
                performance=performance,
                status=AgentStatus.HEALTHY,
                config_hash=self._calculate_config_hash(config)
            )
            
            self.active_agents[agent_id] = generated_agent
            
            self.logger.info(f"✅ Generated agent {agent_id} for {platform}")
            return generated_agent
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate agent for {platform}: {e}")
            raise
    
    async def _create_agent_class(self, platform: str, config: Dict[str, Any]) -> Type:
        """Create agent class dynamically"""
        
        template = self.agent_templates.get(platform, {})
        
        # Dynamic class creation
        class_name = f"{platform.title()}Agent"
        
        # Get base class
        base_class = await self._get_base_class(template.get('base_class', 'BaseSocialAgent'))
        
        # Create class dynamically
        agent_class = type(
            class_name,
            (base_class,),
            {
                'platform': platform,
                'timeout': template.get('timeout', 30),
                'rate_limit': template.get('rate_limit', 10),
                'config': config or {},
                '_template': template,
                '__module__': __name__
            }
        )
        
        # Add required methods
        await self._add_required_methods(agent_class, template)
        
        return agent_class
    
    async def _get_base_class(self, base_class_name: str) -> Type:
        """Get the base class for agent generation"""
        try:
            if base_class_name == 'BaseSocialAgent':
                from .base_agent import BaseSocialAgent
                return BaseSocialAgent
            elif base_class_name == 'BaseCodeAgent':
                from .base_agent import BaseCodeAgent  
                return BaseCodeAgent
            else:
                from .base_agent import BaseAgent
                return BaseAgent
        except ImportError:
            from .base_agent import BaseAgent
            return BaseAgent
    
    async def _add_required_methods(self, agent_class: Type, template: Dict[str, Any]):
        """Add required methods to agent class"""
        required_methods = template.get('required_methods', [])
        
        for method_name in required_methods:
            if not hasattr(agent_class, method_name):
                # Add placeholder method that will be implemented per platform
                setattr(agent_class, method_name, self._create_placeholder_method(method_name))
    
    def _create_placeholder_method(self, method_name: str):
        """Create placeholder method that raises NotImplementedError"""
        async def placeholder_method(self, *args, **kwargs):
            raise NotImplementedError(f"Method {method_name} must be implemented for {self.platform}")
        return placeholder_method
    
    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """Calculate hash of agent configuration for versioning"""
        config_str = json.dumps(config, sort_keys=True) if config else ""
        return hashlib.md5(config_str.encode()).hexdigest()
    
    async def monitor_agent_health(self) -> Dict[str, Any]:
        """Monitor health of all active agents"""
        self.logger.info("🔍 Monitoring agent health...")
        
        health_report = {
            'timestamp': datetime.now(),
            'total_agents': len(self.active_agents),
            'healthy_agents': 0,
            'degraded_agents': 0,
            'failing_agents': 0,
            'agent_details': {},
            'replacements_triggered': 0
        }
        
        agents_to_replace = []
        
        for agent_id, agent in self.active_agents.items():
            # Check agent health
            is_healthy = await self._check_agent_health(agent)
            
            if is_healthy:
                agent.status = AgentStatus.HEALTHY
                health_report['healthy_agents'] += 1
            else:
                agent.status = AgentStatus.FAILING
                health_report['failing_agents'] += 1
                agents_to_replace.append(agent_id)
            
            health_report['agent_details'][agent_id] = {
                'platform': agent.platform,
                'status': agent.status.value,
                'success_rate': agent.performance.success_rate,
                'avg_response_time': agent.performance.avg_response_time,
                'error_rate': agent.performance.error_rate
            }
        
        # Replace failing agents
        for agent_id in agents_to_replace:
            await self._replace_failing_agent(agent_id)
            health_report['replacements_triggered'] += 1
        
        self.logger.info(f"✅ Agent health check: {health_report['healthy_agents']} healthy, {health_report['failing_agents']} failing")
        
        return health_report
    
    async def _check_agent_health(self, agent: GeneratedAgent) -> bool:
        """Check if agent meets health thresholds"""
        perf = agent.performance
        
        if (perf.success_rate < self.performance_thresholds['success_rate_min'] or
            perf.avg_response_time > self.performance_thresholds['response_time_max'] or
            perf.error_rate > self.performance_thresholds['error_rate_max']):
            return False
        
        # Check if agent has been successful recently
        if (perf.last_success and 
            datetime.now() - perf.last_success > timedelta(hours=1) and
            perf.total_requests > 0):
            return False
        
        return True
    
    async def _replace_failing_agent(self, agent_id: str):
        """Replace a failing agent with a new instance"""
        self.logger.warning(f"🔄 Replacing failing agent: {agent_id}")
        
        try:
            old_agent = self.active_agents[agent_id]
            platform = old_agent.platform
            
            # Generate new agent
            new_agent = await self.generate_agent(platform, old_agent.config)
            
            # Replace in active agents
            self.active_agents[agent_id] = new_agent
            
            # Clean up old agent
            await self._cleanup_agent(old_agent)
            
            self.logger.info(f"✅ Replaced agent {agent_id} with {new_agent.agent_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to replace agent {agent_id}: {e}")
    
    async def _cleanup_agent(self, agent: GeneratedAgent):
        """Clean up agent resources"""
        try:
            # Perform any necessary cleanup
            if hasattr(agent.agent_class, 'cleanup'):
                await agent.agent_class.cleanup()
        except Exception as e:
            self.logger.warning(f"⚠️ Agent cleanup failed: {e}")
    
    async def optimize_agents_for_resources(self, resource_strategy: ResourceStrategy):
        """Optimize all agents based on current resource strategy"""
        self.logger.info(f"🎯 Optimizing agents for {resource_strategy.level.value} resources")
        
        for agent_id, agent in self.active_agents.items():
            await self._optimize_individual_agent(agent, resource_strategy)
    
    async def _optimize_individual_agent(self, agent: GeneratedAgent, strategy: ResourceStrategy):
        """Optimize individual agent based on resource strategy"""
        try:
            # Adjust agent timeouts
            if hasattr(agent.agent_class, 'timeout'):
                agent.agent_class.timeout = strategy.agent_timeout
            
            # Adjust rate limiting
            if hasattr(agent.agent_class, 'rate_limit'):
                # Reduce rate limit for lower resource levels
                base_rate = getattr(agent.agent_class, 'base_rate_limit', 10)
                if strategy.level in [ResourceLevel.LOW, ResourceLevel.CRITICAL]:
                    agent.agent_class.rate_limit = max(1, base_rate // 2)
                else:
                    agent.agent_class.rate_limit = base_rate
            
            # Adjust data collection depth
            if hasattr(agent.agent_class, 'data_depth'):
                if strategy.data_quality == 'basic':
                    agent.agent_class.data_depth = 'minimal'
                elif strategy.data_quality == 'standard':
                    agent.agent_class.data_depth = 'normal'
                else:
                    agent.agent_class.data_depth = 'comprehensive'
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to optimize agent {agent.agent_id}: {e}")
    
    def get_agent_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive agent performance report"""
        report = {
            'summary': {
                'total_agents': len(self.active_agents),
                'by_status': {},
                'by_platform': {}
            },
            'performance_metrics': {
                'average_success_rate': 0.0,
                'average_response_time': 0.0,
                'overall_health_score': 0.0
            },
            'recommendations': []
        }
        
        if not self.active_agents:
            return report
        
        # Calculate metrics
        total_success = 0.0
        total_response_time = 0.0
        total_health_score = 0.0
        
        for agent_id, agent in self.active_agents.items():
            # Status distribution
            status = agent.status.value
            report['summary']['by_status'][status] = report['summary']['by_status'].get(status, 0) + 1
            
            # Platform distribution
            platform = agent.platform
            report['summary']['by_platform'][platform] = report['summary']['by_platform'].get(platform, 0) + 1
            
            # Performance metrics
            total_success += agent.performance.success_rate
            total_response_time += agent.performance.avg_response_time
            
            # Health score (0-100)
            health_score = (
                agent.performance.success_rate * 40 +
                max(0, 100 - agent.performance.avg_response_time) * 30 +
                max(0, 100 - agent.performance.error_rate * 100) * 30
            )
            total_health_score += health_score
        
        # Calculate averages
        report['performance_metrics']['average_success_rate'] = total_success / len(self.active_agents)
        report['performance_metrics']['average_response_time'] = total_response_time / len(self.active_agents)
        report['performance_metrics']['overall_health_score'] = total_health_score / len(self.active_agents)
        
        # Generate recommendations
        report['recommendations'] = self._generate_agent_recommendations()
        
        return report
    
    def _generate_agent_recommendations(self) -> List[str]:
        """Generate agent performance recommendations"""
        recommendations = []
        
        failing_count = sum(1 for agent in self.active_agents.values() 
                          if agent.status == AgentStatus.FAILING)
        
        if failing_count > len(self.active_agents) * 0.3:  # More than 30% failing
            recommendations.append("High agent failure rate - investigate platform changes or API issues")
        
        low_success_agents = [a for a in self.active_agents.values() 
                            if a.performance.success_rate < 0.5]
        if low_success_agents:
            recommendations.append(f"{len(low_success_agents)} agents with low success rate - consider regeneration")
        
        return recommendations

# Global agent generator instance
agent_generator = AgentGenerator()
