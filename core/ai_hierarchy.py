# In core/ai_hierarchy.py - Add to __init__ method
"""
AI HIERARCHY MANAGEMENT SYSTEM
Orchestrates multiple AI agents with oversight, validation, and continuous learning
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
from collections import defaultdict
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import DBSCAN
import joblib
import pickle

class AIAgentRole(Enum):
    COLLECTOR = "collector"           # Data gathering agents
    ANALYZER = "analyzer"             # Pattern analysis agents  
    VALIDATOR = "validator"           # Cross-validation agents
    CORRELATOR = "correlator"         # Relationship mapping agents
    DECISION_MAKER = "decision_maker" # Final judgment agents
    OVERSIGHT = "oversight"           # Quality control agents

class AgentPerformance(Enum):
    EXCELLENT = "excellent"    # 90%+ accuracy
    GOOD = "good"              # 80-89% accuracy
    FAIR = "fair"              # 70-79% accuracy
    POOR = "poor"              # <70% accuracy
    DEGRADED = "degraded"      # System issues

@dataclass
class AgentMetrics:
    success_rate: float
    average_confidence: float
    response_time: float
    error_rate: float
    data_quality: float
    last_calibration: datetime

@dataclass
class AIDecision:
    primary_decision: Any
    confidence: float
    supporting_evidence: List[Any]
    dissenting_opinions: List[Any]
    quality_score: float
    decision_tree: Dict[str, Any]

class AIHierarchyManager:
    """
    ENTERPRISE AI HIERARCHY MANAGEMENT
    Orchestrates multiple AI agents with oversight and continuous learning
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ai_hierarchy")
        
        # Agent registry by role
        self.agent_registry = {
            AIAgentRole.COLLECTOR: {},
            AIAgentRole.ANALYZER: {},
            AIAgentRole.VALIDATOR: {},
            AIAgentRole.CORRELATOR: {},
            AIAgentRole.DECISION_MAKER: {},
            AIAgentRole.OVERSIGHT: {}
        }
        
        # Performance tracking
        self.agent_metrics = {}
        self.performance_history = defaultdict(list)
        
        # ML Models
        self.behavioral_cluster_model = None
        self.performance_predictor = None
        self.quality_assessor = None
        
        # Bunker system
        self.analysis_bunker = AnalysisBunker()
        
        # Initialize ML models
        self._initialize_ml_models()
        
        self.logger.info("👑 AI Hierarchy Manager initialized")
    
    def register_agent(self, agent_id: str, agent_instance: Any, role: AIAgentRole, 
                      capabilities: List[str], weight: float = 1.0):
        """Register an AI agent in the hierarchy"""
        self.agent_registry[role][agent_id] = {
            'instance': agent_instance,
            'capabilities': capabilities,
            'weight': weight,
            'registered_at': datetime.now(),
            'performance': AgentMetrics(
                success_rate=0.0,
                average_confidence=0.0,
                response_time=0.0,
                error_rate=0.0,
                data_quality=0.0,
                last_calibration=datetime.now()
            )
        }
        
        self.logger.info(f"✅ Registered agent {agent_id} as {role.value}")
    
    async def orchestrate_analysis(self, target: str, context: Dict[str, Any]) -> AIDecision:
        """
        Orchestrate multi-agent analysis with hierarchical decision making
        """
        analysis_id = f"analysis_{hashlib.md5(target.encode()).hexdigest()[:8]}"
        
        self.logger.info(f"🎯 Orchestrating hierarchical analysis for: {target}")
        
        # Phase 1: Data Collection
        collection_results = await self._execute_collection_phase(target, context)
        
        # Phase 2: Multi-dimensional Analysis
        analysis_results = await self._execute_analysis_phase(collection_results, context)
        
        # Phase 3: Cross-Validation
        validation_results = await self._execute_validation_phase(analysis_results)
        
        # Phase 4: Correlation & Pattern Recognition
        correlation_results = await self._execute_correlation_phase(validation_results)
        
        # Phase 5: Hierarchical Decision Making
        final_decision = await self._execute_decision_phase(correlation_results)
        
        # Phase 6: Oversight & Quality Control
        quality_assured_decision = await self._execute_oversight_phase(final_decision)
        
        # Store in bunker for future learning
        await self.analysis_bunker.store_analysis(analysis_id, {
            'target': target,
            'collection_results': collection_results,
            'analysis_results': analysis_results,
            'final_decision': quality_assured_decision,
            'timestamp': datetime.now()
        })
        
        # Update agent performance metrics
        await self._update_agent_performance(analysis_id)
        
        return quality_assured_decision
    
    async def _execute_collection_phase(self, target: str, context: Dict) -> Dict[str, Any]:
        """Execute data collection using collector agents"""
        self.logger.info("📥 Phase 1: Data Collection")
        
        collection_tasks = []
        collector_agents = self.agent_registry[AIAgentRole.COLLECTOR]
        
        for agent_id, agent_data in collector_agents.items():
            task = self._execute_agent_with_oversight(
                agent_data, 'collect_data', target, context
            )
            collection_tasks.append((agent_id, task))
        
        # Execute all collectors concurrently
        results = {}
        for agent_id, task in collection_tasks:
            try:
                result = await task
                results[agent_id] = result
            except Exception as e:
                self.logger.error(f"❌ Collector {agent_id} failed: {e}")
                results[agent_id] = {'error': str(e)}
        
        return {
            'raw_data': results,
            'collection_timestamp': datetime.now(),
            'successful_collectors': [aid for aid, res in results.items() if 'error' not in res]
        }
    
    async def _execute_analysis_phase(self, collection_results: Dict, context: Dict) -> Dict[str, Any]:
        """Execute multi-dimensional analysis using analyzer agents"""
        self.logger.info("🔍 Phase 2: Multi-dimensional Analysis")
        
        analysis_tasks = []
        analyzer_agents = self.agent_registry[AIAgentRole.ANALYZER]
        
        for agent_id, agent_data in analyzer_agents.items():
            task = self._execute_agent_with_oversight(
                agent_data, 'analyze_data', collection_results, context
            )
            analysis_tasks.append((agent_id, task))
        
        analysis_results = {}
        for agent_id, task in analysis_tasks:
            try:
                result = await task
                analysis_results[agent_id] = result
            except Exception as e:
                self.logger.error(f"❌ Analyzer {agent_id} failed: {e}")
        
        # Apply ML-based analysis aggregation
        aggregated_analysis = await self._aggregate_analysis_with_ml(analysis_results)
        
        return {
            'individual_analyses': analysis_results,
            'aggregated_analysis': aggregated_analysis,
            'analysis_consensus': await self._calculate_analysis_consensus(analysis_results)
        }
    
    async def _execute_validation_phase(self, analysis_results: Dict) -> Dict[str, Any]:
        """Execute cross-validation using validator agents"""
        self.logger.info("✅ Phase 3: Cross-Validation")
        
        validation_tasks = []
        validator_agents = self.agent_registry[AIAgentRole.VALIDATOR]
        
        for agent_id, agent_data in validator_agents.items():
            task = self._execute_agent_with_oversight(
                agent_data, 'validate_analysis', analysis_results
            )
            validation_tasks.append((agent_id, task))
        
        validation_results = {}
        for agent_id, task in validation_tasks:
            try:
                result = await task
                validation_results[agent_id] = result
            except Exception as e:
                self.logger.error(f"❌ Validator {agent_id} failed: {e}")
        
        # Calculate validation confidence
        validation_confidence = await self._calculate_validation_confidence(validation_results)
        
        return {
            'validation_results': validation_results,
            'overall_confidence': validation_confidence,
            'flagged_issues': await self._identify_validation_issues(validation_results)
        }
    
    async def _execute_correlation_phase(self, validation_results: Dict) -> Dict[str, Any]:
        """Execute pattern correlation using correlator agents"""
        self.logger.info("🔄 Phase 4: Pattern Correlation")
        
        correlation_tasks = []
        correlator_agents = self.agent_registry[AIAgentRole.CORRELATOR]
        
        for agent_id, agent_data in correlator_agents.items():
            task = self._execute_agent_with_oversight(
                agent_data, 'correlate_patterns', validation_results
            )
            correlation_tasks.append((agent_id, task))
        
        correlation_results = {}
        for agent_id, task in correlation_tasks:
            try:
                result = await task
                correlation_results[agent_id] = result
            except Exception as e:
                self.logger.error(f"❌ Correlator {agent_id} failed: {e}")
        
        # Apply ML-based pattern recognition
        ml_correlations = await self._apply_ml_correlation(correlation_results)
        
        return {
            'agent_correlations': correlation_results,
            'ml_enhanced_correlations': ml_correlations,
            'pattern_confidence': await self._calculate_pattern_confidence(correlation_results)
        }
    
    async def _execute_decision_phase(self, correlation_results: Dict) -> AIDecision:
        """Execute hierarchical decision making"""
        self.logger.info("🎯 Phase 5: Hierarchical Decision Making")
        
        decision_tasks = []
        decision_agents = self.agent_registry[AIAgentRole.DECISION_MAKER]
        
        for agent_id, agent_data in decision_agents.items():
            task = self._execute_agent_with_oversight(
                agent_data, 'make_decision', correlation_results
            )
            decision_tasks.append((agent_id, task))
        
        agent_decisions = {}
        for agent_id, task in decision_tasks:
            try:
                result = await task
                agent_decisions[agent_id] = result
            except Exception as e:
                self.logger.error(f"❌ Decision agent {agent_id} failed: {e}")
        
        # Weighted decision aggregation
        final_decision = await self._aggregate_decisions(agent_decisions)
        
        return final_decision
    
    async def _execute_oversight_phase(self, decision: AIDecision) -> AIDecision:
        """Execute quality control and oversight"""
        self.logger.info("👑 Phase 6: Quality Oversight")
        
        oversight_tasks = []
        oversight_agents = self.agent_registry[AIAgentRole.OVERSIGHT]
        
        for agent_id, agent_data in oversight_agents.items():
            task = self._execute_agent_with_oversight(
                agent_data, 'review_decision', decision
            )
            oversight_tasks.append((agent_id, task))
        
        oversight_reviews = {}
        for agent_id, task in oversight_tasks:
            try:
                result = await task
                oversight_reviews[agent_id] = result
            except Exception as e:
                self.logger.error(f"❌ Oversight agent {agent_id} failed: {e}")
        
        # Apply oversight adjustments
        quality_assured_decision = await self._apply_oversight_corrections(decision, oversight_reviews)
        
        return quality_assured_decision
    
    async def _execute_agent_with_oversight(self, agent_data: Dict, method: str, *args) -> Any:
        """Execute agent method with performance monitoring and error handling"""
        agent = agent_data['instance']
        agent_id = [k for k, v in self.agent_registry.items() if agent_data in v.values()][0]
        
        start_time = time.time()
        
        try:
            if hasattr(agent, method):
                result = await getattr(agent, method)(*args)
                
                # Update performance metrics
                execution_time = time.time() - start_time
                await self._update_agent_metrics(agent_id, execution_time, True)
                
                return result
            else:
                raise AttributeError(f"Agent {agent_id} missing method {method}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            await self._update_agent_metrics(agent_id, execution_time, False)
            raise
    
    async def _aggregate_analysis_with_ml(self, analysis_results: Dict) -> Dict[str, Any]:
        """Aggregate analysis results using ML-based weighting"""
        # Use agent performance history to weight their analyses
        weighted_analyses = {}
        
        for agent_id, analysis in analysis_results.items():
            agent_performance = self.agent_metrics.get(agent_id, {}).get('success_rate', 0.5)
            weight = agent_performance  # Higher performance = higher weight
            
            # Apply weight to analysis confidence
            if 'confidence' in analysis:
                analysis['weighted_confidence'] = analysis['confidence'] * weight
            
            weighted_analyses[agent_id] = analysis
        
        # Cluster similar analyses
        analysis_clusters = await self._cluster_similar_analyses(weighted_analyses)
        
        return {
            'weighted_analyses': weighted_analyses,
            'analysis_clusters': analysis_clusters,
            'consensus_analysis': await self._find_analysis_consensus(analysis_clusters)
        }
    
    async def _cluster_similar_analyses(self, analyses: Dict) -> List[List[str]]:
        """Cluster similar analyses using ML clustering"""
        if not analyses:
            return []
        
        # Convert analyses to feature vectors
        feature_vectors = []
        agent_ids = list(analyses.keys())
        
        for agent_id in agent_ids:
            analysis = analyses[agent_id]
            features = self._analysis_to_features(analysis)
            feature_vectors.append(features)
        
        if len(feature_vectors) < 2:
            return [agent_ids]
        
        # Apply clustering
        clustering = DBSCAN(eps=0.5, min_samples=1)
        clusters = clustering.fit_predict(feature_vectors)
        
        # Group agent IDs by cluster
        cluster_groups = defaultdict(list)
        for agent_id, cluster_id in zip(agent_ids, clusters):
            cluster_groups[cluster_id].append(agent_id)
        
        return list(cluster_groups.values())
    
    def _analysis_to_features(self, analysis: Dict) -> List[float]:
        """Convert analysis to feature vector for clustering"""
        features = []
        
        # Confidence feature
        features.append(analysis.get('confidence', 0.5))
        
        # Data completeness feature
        features.append(analysis.get('data_completeness', 0.5))
        
        # Pattern strength feature
        features.append(analysis.get('pattern_strength', 0.5))
        
        # Timeliness feature (recent analysis gets higher weight)
        if 'timestamp' in analysis:
            recency = (datetime.now() - analysis['timestamp']).total_seconds() / 3600
            features.append(max(0, 1 - recency / 24))  # Decay over 24 hours
        else:
            features.append(0.5)
        
        return features
    
    async def _aggregate_decisions(self, agent_decisions: Dict) -> AIDecision:
        """Aggregate decisions with ML-based confidence weighting"""
        if not agent_decisions:
            return AIDecision(
                primary_decision=None,
                confidence=0.0,
                supporting_evidence=[],
                dissenting_opinions=[],
                quality_score=0.0,
                decision_tree={}
            )
        
        # Weight decisions by agent performance
        weighted_decisions = []
        total_weight = 0
        
        for agent_id, decision in agent_decisions.items():
            agent_weight = self.agent_metrics.get(agent_id, {}).get('success_rate', 0.5)
            weighted_decisions.append({
                'decision': decision,
                'weight': agent_weight,
                'agent_id': agent_id
            })
            total_weight += agent_weight
        
        if total_weight == 0:
            total_weight = 1  # Prevent division by zero
        
        # Find consensus decision
        consensus_decision = await self._find_consensus_decision(weighted_decisions)
        
        return AIDecision(
            primary_decision=consensus_decision['decision'],
            confidence=consensus_decision['confidence'],
            supporting_evidence=consensus_decision['supporting_evidence'],
            dissenting_opinions=consensus_decision['dissenting_opinions'],
            quality_score=consensus_decision['quality_score'],
            decision_tree=consensus_decision['decision_tree']
        )
    
    async def _find_consensus_decision(self, weighted_decisions: List[Dict]) -> Dict[str, Any]:
        """Find consensus among weighted decisions"""
        # Group similar decisions
        decision_groups = defaultdict(list)
        
        for wd in weighted_decisions:
            decision_hash = hashlib.md5(str(wd['decision']).encode()).hexdigest()
            decision_groups[decision_hash].append(wd)
        
        # Find group with highest total weight
        best_group = None
        max_weight = 0
        
        for group_hash, decisions in decision_groups.items():
            group_weight = sum(d['weight'] for d in decisions)
            if group_weight > max_weight:
                max_weight = group_weight
                best_group = decisions
        
        if not best_group:
            return {'decision': None, 'confidence': 0.0, 'supporting_evidence': [], 
                    'dissenting_opinions': [], 'quality_score': 0.0, 'decision_tree': {}}
        
        # Calculate confidence based on group weight and agreement
        total_possible_weight = sum(d['weight'] for d in weighted_decisions)
        confidence = max_weight / total_possible_weight if total_possible_weight > 0 else 0
        
        # Collect supporting and dissenting evidence
        supporting_evidence = [d for d in weighted_decisions if d in best_group]
        dissenting_opinions = [d for d in weighted_decisions if d not in best_group]
        
        return {
            'decision': best_group[0]['decision'],
            'confidence': confidence,
            'supporting_evidence': supporting_evidence,
            'dissenting_opinions': dissenting_opinions,
            'quality_score': confidence * len(best_group) / len(weighted_decisions),
            'decision_tree': {'consensus_group': best_group, 'all_groups': decision_groups}
        }
    
    async def _update_agent_metrics(self, agent_id: str, execution_time: float, success: bool):
        """Update agent performance metrics"""
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = {
                'success_count': 0,
                'tota
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
