"""
ANALYSIS BUNKER SYSTEM
Deep storage and ML-powered pattern recognition for historical analysis
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import sqlite3
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

@dataclass
class BunkerAnalysis:
    analysis_id: str
    target: str
    analysis_data: Dict[str, Any]
    timestamp: datetime
    patterns_detected: List[str]
    similarity_score: float
    cluster_assignment: int

class AnalysisBunker:
    """
    DEEP ANALYSIS BUNKER
    Stores and analyzes historical data for pattern recognition
    """
    
    def __init__(self, bunker_path: str = "data/analysis_bunker.db"):
        self.bunker_path = Path(bunker_path)
        self.bunker_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("analysis_bunker")
        
        # ML Components
        self.behavior_cluster_model = KMeans(n_clusters=10)
        self.similarity_vectorizer = TfidfVectorizer(max_features=1000)
        self.pattern_detector = None
        
        # Initialize database
        self._init_database()
        self._load_ml_models()
        
        self.logger.info("🏰 Analysis Bunker initialized")
    
    def _init_database(self):
        """Initialize bunker database"""
        conn = sqlite3.connect(self.bunker_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                analysis_id TEXT PRIMARY KEY,
                target TEXT NOT NULL,
                analysis_data TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                patterns_detected TEXT,
                similarity_score REAL,
                cluster_assignment INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavioral_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence REAL,
                first_detected DATETIME,
                last_seen DATETIME,
                occurrence_count INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS similarity_index (
                source_id TEXT,
                target_id TEXT,
                similarity_score REAL,
                comparison_type TEXT,
                PRIMARY KEY (source_id, target_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def store_analysis(self, analysis_id: str, analysis_data: Dict[str, Any]):
        """Store analysis in bunker and process for patterns"""
        self.logger.info(f"💾 Storing analysis {analysis_id} in bunker")
        
        # Store in database
        conn = sqlite3.connect(self.bunker_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO analyses 
            (analysis_id, target, analysis_data, timestamp, patterns_detected, similarity_score, cluster_assignment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_id,
            analysis_data.get('target', ''),
            json.dumps(analysis_data, default=str),
            analysis_data.get('timestamp', datetime.now()),
            json.dumps([]),  # Will be updated after pattern detection
            0.0,  # Will be updated after similarity analysis
            -1  # Will be updated after clustering
        ))
        
        conn.commit()
        conn.close()
        
        # Process for patterns and similarities
        await self._process_new_analysis(analysis_id, analysis_data)
    
    async def _process_new_analysis(self, analysis_id: str, analysis_data: Dict[str, Any]):
        """Process new analysis for patterns and similarities"""
        # 1. Detect behavioral patterns
        patterns = await self._detect_behavioral_patterns(analysis_data)
        
        # 2. Calculate similarity with existing analyses
        similarities = await self._calculate_similarities(analysis_id, analysis_data)
        
        # 3. Assign to behavioral cluster
        cluster_id = await self._assign_to_cluster(analysis_data)
        
        # 4. Update database with processed information
        conn = sqlite3.connect(self.bunker_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE analyses 
            SET patterns_detected = ?, similarity_score = ?, cluster_assignment = ?
            WHERE analysis_id = ?
        ''', (
            json.dumps(patterns),
            max([s['score'] for s in similarities]) if similarities else 0.0,
            cluster_id,
            analysis_id
        ))
        
        # Store similarities
        for similarity in similarities:
            cursor.execute('''
                INSERT OR REPLACE INTO similarity_index 
                (source_id, target_id, similarity_score, comparison_type)
                VALUES (?, ?, ?, ?)
            ''', (analysis_id, similarity['target_id'], similarity['score'], similarity['type']))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"✅ Processed analysis {analysis_id}: {len(patterns)} patterns, cluster {cluster_id}")
    
    async def _detect_behavioral_patterns(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Detect behavioral patterns in analysis data"""
        patterns = []
        
        # Extract key behavioral indicators
        behavioral_data = analysis_data.get('behavioral_analysis', {})
        deception_data = analysis_data.get('deception_analysis', {})
        
        # Pattern 1: Activity timing patterns
        activity_patterns = behavioral_data.get('platform_usage_patterns', {})
        if len(activity_patterns) > 5:  # Active on many platforms
            patterns.append("HIGH_PLATFORM_DIVERSITY")
        
        # Pattern 2: Deception indicators
        if deception_data.get('overall_risk_score', 0) > 0.7:
            patterns.append("HIGH_DECEPTION_RISK")
        
        # Pattern 3: Geographic patterns
        locations = self._extract_locations(analysis_data)
        if len(locations) > 2:
            patterns.append("MULTI_GEOGRAPHIC_PRESENCE")
        
        # Pattern 4: Temporal patterns
        if self._detect_nocturnal_pattern(behavioral_data):
            patterns.append("NOCTURNAL_ACTIVITY")
        
        # Pattern 5: Content patterns
        content_patterns = self._analyze_content_patterns(analysis_data)
        patterns.extend(content_patterns)
        
        # Store new patterns
        await self._store_new_patterns(patterns, analysis_data)
        
        return patterns
    
    async def _calculate_similarities(self, new_analysis_id: str, new_analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate similarity with existing analyses"""
        similarities = []
        
        # Get recent analyses for comparison
        recent_analyses = await self._get_recent_analyses(limit=100)
        
        for existing_analysis in recent_analyses:
            if existing_analysis['analysis_id'] == new_analysis_id:
                continue
            
            similarity_score = await self._calculate_analysis_similarity(
                new_analysis_data, existing_analysis['analysis_data']
            )
            
            if similarity_score > 0.6: 
