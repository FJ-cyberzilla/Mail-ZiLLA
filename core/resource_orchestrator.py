"""
ADAPTIVE RESOURCE ORCHESTRATOR
Dynamically manages system resources based on network speed, memory, and performance
"""

import asyncio
import psutil
import speedtest
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta

class ResourceLevel(Enum):
    CRITICAL = "critical"      # Very limited resources
    LOW = "low"                # Limited resources  
    MEDIUM = "medium"          # Normal resources
    HIGH = "high"              # Good resources
    EXCELLENT = "excellent"    # Excellent resources

@dataclass
class SystemResources:
    memory_available: float    # GB
    memory_usage: float        # Percentage
    cpu_usage: float          # Percentage
    disk_available: float     # GB
    network_speed: float      # Mbps
    battery_level: float      # Percentage (if applicable)

@dataclass
class ResourceStrategy:
    level: ResourceLevel
    max_concurrent_tasks: int
    agent_timeout: int
    proxy_usage: str          # 'minimal', 'balanced', 'aggressive'
    data_quality: str         # 'basic', 'standard', 'comprehensive'
    caching_strategy: str     # 'minimal', 'balanced', 'aggressive'

class AdaptiveResourceOrchestrator:
    """
    Adaptive Resource Management for Enterprise Performance
    Dynamically adjusts resource usage based on system capabilities
    """
    
    def __init__(self):
        self.logger = logging.getLogger("resource_orchestrator")
        self.performance_history = []
        self.current_strategy = None
        self.last_network_test = None
        self.network_speed_cache = None
        
    async def assess_system_resources(self) -> SystemResources:
        """Comprehensive system resource assessment"""
        self.logger.info("🔍 Assessing system resources...")
        
        # Get system metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Get network speed (cached to avoid frequent testing)
        network_speed = await self._get_network_speed()
        
        # Get battery level if available
        try:
            battery = psutil.sensors_battery()
            battery_level = battery.percent if battery else 100.0
        except:
            battery_level = 100.0  # Assume desktop
        
        resources = SystemResources(
            memory_available=memory.available / (1024**3),  # Convert to GB
            memory_usage=memory.percent,
            cpu_usage=cpu_usage,
            disk_available=disk.free / (1024**3),  # Convert to GB
            network_speed=network_speed,
            battery_level=battery_level
        )
        
        self.performance_history.append({
            'timestamp': datetime.now(),
            'resources': resources,
            'strategy_applied': self.current_strategy.level if self.current_strategy else None
        })
        
        # Keep only last 100 records
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
        
        return resources
    
    async def _get_network_speed(self) -> float:
        """Get current network speed with caching"""
        # Cache network speed for 5 minutes to avoid frequent testing
        if (self.network_speed_cache and 
            self.last_network_test and 
            datetime.now() - self.last_network_test < timedelta(minutes=5)):
            return self.network_speed_cache
        
        try:
            self.logger.info("🌐 Testing network speed...")
            st = speedtest.Speedtest()
            st.get_best_server()
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            
            self.network_speed_cache = download_speed
            self.last_network_test = datetime.now()
            
            self.logger.info(f"✅ Network speed: {download_speed:.1f} Mbps")
            return download_speed
            
        except Exception as e:
            self.logger.warning(f"⚠️ Network speed test failed: {e}")
            # Return conservative estimate
            return 10.0  # Assume 10 Mbps
    
    def determine_resource_strategy(self, resources: SystemResources) -> ResourceStrategy:
        """Determine optimal resource strategy based on available resources"""
        
        # Calculate resource scores (0-100)
        memory_score = max(0, 100 - resources.memory_usage)  # Higher available memory = better
        cpu_score = max(0, 100 - resources.cpu_usage)
        network_score = min(100, resources.network_speed * 2)  # 50 Mbps = 100 score
        battery_score = resources.battery_level
        
        # Weighted overall score
        overall_score = (
            memory_score * 0.3 +
            cpu_score * 0.3 + 
            network_score * 0.3 +
            battery_score * 0.1
        )
        
        # Determine resource level
        if overall_score >= 80:
            level = ResourceLevel.EXCELLENT
        elif overall_score >= 60:
            level = ResourceLevel.HIGH
        elif overall_score >= 40:
            level = ResourceLevel.MEDIUM
        elif overall_score >= 20:
            level = ResourceLevel.LOW
        else:
            level = ResourceLevel.CRITICAL
        
        strategy = self._create_strategy_for_level(level, resources)
        self.current_strategy = strategy
        
        self.logger.info(f"🎯 Resource strategy: {level.value} (score: {overall_score:.1f})")
        
        return strategy
    
    def _create_strategy_for_level(self, level: ResourceLevel, resources: SystemResources) -> ResourceStrategy:
        """Create resource strategy for specific resource level"""
        
        strategies = {
            ResourceLevel.EXCELLENT: ResourceStrategy(
                level=level,
                max_concurrent_tasks=8,
                agent_timeout=30,
                proxy_usage='aggressive',
                data_quality='comprehensive',
                caching_strategy='aggressive'
            ),
            ResourceLevel.HIGH: ResourceStrategy(
                level=level,
                max_concurrent_tasks=6,
                agent_timeout=25,
                proxy_usage='balanced',
                data_quality='comprehensive',
                caching_strategy='balanced'
            ),
            ResourceLevel.MEDIUM: ResourceStrategy(
                level=level,
                max_concurrent_tasks=4,
                agent_timeout=20,
                proxy_usage='balanced',
                data_quality='standard',
                caching_strategy='balanced'
            ),
            ResourceLevel.LOW: ResourceStrategy(
                level=level,
                max_concurrent_tasks=2,
                agent_timeout=15,
                proxy_usage='minimal',
                data_quality='basic',
                caching_strategy='minimal'
            ),
            ResourceLevel.CRITICAL: ResourceStrategy(
                level=level,
                max_concurrent_tasks=1,
                agent_timeout=10,
                proxy_usage='minimal',
                data_quality='basic',
                caching_strategy='minimal'
            )
        }
        
        return strategies[level]
    
    async def optimize_agent_operations(self, strategy: ResourceStrategy) -> Dict[str, Any]:
        """Optimize agent operations based on resource strategy"""
        
        optimizations = {
            'concurrency_limits': {
                'max_platform_agents': strategy.max_concurrent_tasks,
                'max_proxy_checks': min(5, strategy.max_concurrent_tasks),
                'max_parallel_requests': strategy.max_concurrent_tasks * 2
            },
            'timeout_settings': {
                'agent_timeout': strategy.agent_timeout,
                'proxy_timeout': strategy.agent_timeout - 5,
                'http_timeout': strategy.agent_timeout - 10
            },
            'data_quality': {
                'enable_image_analysis': strategy.data_quality in ['comprehensive', 'standard'],
                'enable_advanced_correlation': strategy.data_quality == 'comprehensive',
                'enable_fingerprinting': strategy.data_quality == 'comprehensive',
                'max_profiles_per_platform': 50 if strategy.data_quality == 'comprehensive' else 20
            },
            'caching': {
                'enable_memory_cache': strategy.caching_strategy != 'minimal',
                'enable_disk_cache': True,
                'cache_ttl_minutes': 60 if strategy.caching_strategy == 'aggressive' else 30
            },
            'proxy_management': {
                'proxy_rotation_frequency': 'high' if strategy.proxy_usage == 'aggressive' else 'medium',
                'max_proxy_retries': 3 if strategy.proxy_usage == 'aggressive' else 2,
                'proxy_health_check_interval': 300 if strategy.proxy_usage == 'aggressive' else 600
            }
        }
        
        return optimizations
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance and resource utilization report"""
        if not self.performance_history:
            return {'status': 'no_data'}
        
        recent_performance = self.performance_history[-10:]  # Last 10 measurements
        
        avg_memory_usage = sum(p['resources'].memory_usage for p in recent_performance) / len(recent_performance)
        avg_cpu_usage = sum(p['resources'].cpu_usage for p in recent_performance) / len(recent_performance)
        avg_network_speed = sum(p['resources'].network_speed for p in recent_performance) / len(recent_performance)
        
        current_strategy = self.current_strategy.level.value if self.current_strategy else 'unknown'
        
        return {
            'current_strategy': current_strategy,
            'average_metrics': {
                'memory_usage_percent': round(avg_memory_usage, 1),
                'cpu_usage_percent': round(avg_cpu_usage, 1),
                'network_speed_mbps': round(avg_network_speed, 1)
            },
            'recommendations': self._generate_performance_recommendations(),
            'resource_trend': self._analyze_resource_trend()
        }
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if not self.performance_history:
            return recommendations
        
        current_resources = self.performance_history[-1]['resources']
        
        if current_resources.memory_usage > 80:
            recommendations.append("Reduce concurrent tasks to lower memory usage")
        
        if current_resources.cpu_usage > 75:
            recommendations.append("Limit CPU-intensive operations")
        
        if current_resources.network_speed < 5:
            recommendations.append("Use minimal data transfer mode for slow network")
        
        if current_resources.battery_level < 20:
            recommendations.append("Switch to power-saving mode")
        
        return recommendations
    
    def _analyze_resource_trend(self) -> str:
        """Analyze resource usage trend"""
        if len(self.performance_history) < 5:
            return "insufficient_data"
        
        recent = self.performance_history[-5:]
        older = self.performance_history[-10:-5]
        
        if not older:  # Not enough history
            return "stable"
        
        avg_recent_memory = sum(p['resources'].memory_usage for p in recent) / len(recent)
        avg_older_memory = sum(p['resources'].memory_usage for p in older) / len(older)
        
        if avg_recent_memory > avg_older_memory + 10:
            return "increasing"
        elif avg_recent_memory < avg_older_memory - 10:
            return "decreasing"
        else:
            return "stable"

# Global resource orchestrator instance
resource_orchestrator = AdaptiveResourceOrchestrator()
