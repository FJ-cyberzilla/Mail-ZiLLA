"""
DATABASE MODELS - SQLAlchemy Schema Definitions
Enterprise-grade data models for Cyberzilla platform
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, JSON, Text, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class TaskResult(Base):
    """Main task results table"""
    __tablename__ = "task_results"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True, index=True)
    
    # Results
    profiles_found = Column(JSON)  # List of found profiles
    confidence_score = Column(Float, default=0.0)
    correlation_evidence = Column(JSON)
    digital_footprint = Column(JSON)
    deception_analysis = Column(JSON)
    behavioral_analysis = Column(JSON)
    
    # Status
    status = Column(String(50), default='pending')  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Metadata
    processing_time = Column(Float)  # Seconds
    agent_versions = Column(JSON)
    platform_coverage = Column(JSON)
    
    # Indexes
    __table_args__ = (
        {'postgresql_partition_by': 'RANGE (created_at)'} if 'postgresql' in str(Base.metadata.bind.engine.url) else {}
    )

class ProxyPool(Base):
    """Proxy pool management"""
    __tablename__ = "proxy_pool"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    proxy_url = Column(String(500), nullable=False, unique=True)
    proxy_type = Column(String(50), default='residential')  # residential, datacenter, mobile
    
    # Status
    is_active = Column(Boolean, default=True)
    last_health_check = Column(DateTime(timezone=True))
    health_status = Column(String(50), default='unknown')  # healthy, degraded, failed
    success_rate = Column(Float, default=0.0)
    avg_response_time = Column(Float, default=0.0)
    
    # Usage
    total_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True))
    
    # Geolocation
    country = Column(String(100))
    city = Column(String(100))
    isp = Column(String(200))
    
    # Security
    is_blacklisted = Column(Boolean, default=False)
    blacklist_reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AgentConfig(Base):
    """AI Agent configurations"""
    __tablename__ = "agent_configs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    agent_name = Column(String(100), nullable=False, unique=True)
    platform = Column(String(50), nullable=False)  # linkedin, github, etc.
    
    # Configuration
    config_data = Column(JSON)  # Agent-specific settings
    is_enabled = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=10)  # requests per minute
    timeout = Column(Integer, default=30)  # seconds
    
    # Performance
    success_rate = Column(Float, default=0.0)
    avg_processing_time = Column(Float, default=0.0)
    last_calibration = Column(DateTime(timezone=True))
    
    # Versioning
    version = Column(String(50), default='1.0.0')
    model_version = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    """User management"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(200))
    role = Column(String(50), default='analyst')  # admin, analyst, viewer
    is_active = Column(Boolean, default=True)
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime(timezone=True))
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(100))
    
    # Preferences
    preferences = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AuditLog(Base):
    """Security audit logs"""
    __tablename__ = "audit_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.id'))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(36))
    
    # Details
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    request_data = Column(JSON)
    response_data = Column(JSON)
    
    # Status
    status = Column(String(50), default='success')  # success, failed
    error_message = Column(Text)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")

class BunkerAnalysis(Base):
    """Analysis bunker storage"""
    __tablename__ = "bunker_analyses"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(100), nullable=False, unique=True, index=True)
    target = Column(String(255), nullable=False, index=True)  # email or phone
    
    # Analysis Data
    analysis_data = Column(JSON, nullable=False)
    patterns_detected = Column(JSON)
    similarity_score = Column(Float, default=0.0)
    cluster_assignment = Column(Integer, default=-1)
    
    # Behavioral Data
    behavioral_signature = Column(JSON)
    deception_indicators = Column(JSON)
    risk_assessment = Column(JSON)
    
    # Timestamps
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Index for performance
    __table_args__ = (
        Index('idx_bunker_target_analyzed', 'target', 'analyzed_at'),
        Index('idx_bunker_cluster', 'cluster_assignment'),
        Index('idx_bunker_similarity', 'similarity_score'),
    )

class PlatformAgent(Base):
    """Platform-specific agent tracking"""
    __tablename__ = "platform_agents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    platform = Column(String(50), nullable=False, unique=True)
    agent_class = Column(String(200), nullable=False)
    
    # Status
    is_available = Column(Boolean, default=True)
    last_health_check = Column(DateTime(timezone=True))
    health_status = Column(String(50), default='unknown')
    
    # Performance Metrics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_response_time = Column(Float, default=0.0)
    
    # Configuration
    config_hash = Column(String(64))  # SHA256 of config
    version = Column(String(50))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RateLimit(Base):
    """Rate limiting tracking"""
    __tablename__ = "rate_limits"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    identifier = Column(String(255), nullable=False, index=True)  # email, IP, user_id
    window_type = Column(String(20), nullable=False)  # minute, hour, day
    request_count = Column(Integer, default=0)
    window_start = Column(DateTime(timezone=True), nullable=False)
    
    # Metadata
    resource = Column(String(100))  # API endpoint, task type
    user_id = Column(String(36), ForeignKey('users.id'))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_rate_limit_identifier_window', 'identifier', 'window_type', 'window_start'),
    )

class SystemMetrics(Base):
    """System performance metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    metric_type = Column(String(100), nullable=False)  # cpu, memory, response_time
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))
    
    # Context
    component = Column(String(100))  # api, worker, database
    node_id = Column(String(100))  # For distributed systems
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_metrics_type_timestamp', 'metric_type', 'timestamp'),
        Index('idx_metrics_component', 'component', 'timestamp'),
    )

# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
