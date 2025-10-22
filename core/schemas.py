"""
PYDANTIC SCHEMAS - Data Validation Models
Enterprise-grade request/response validation for API and internal use
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

class PlatformType(str, Enum):
    LINKEDIN = "linkedin"
    GITHUB = "github"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    SIGNAL = "signal"
    MICROSOFT_TEAMS = "microsoft_teams"
    SKYPE = "skype"
    SLACK = "slack"
    GOOGLE_CHAT = "google_chat"
    DISCORD = "discord"
    REDDIT = "reddit"
    TWITCH = "twitch"
    TIKTOK = "tiktok"
    PINTEREST = "pinterest"
    BLUESKY = "bluesky"
    THREADS = "threads"
    MASTODON = "mastodon"
    ONLYFANS = "onlyfans"
    TUMBLR = "tumblr"
    FLICKR = "flickr"
    FETLIFE = "fetlife"
    PLURK = "plurk"
    VK = "vk"
    WECHAT = "wechat"

# Request Schemas
class LookupRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    advanced_analysis: bool = Field(default=False, description="Enable digital fingerprinting")
    collect_fingerprint: bool = Field(default=True, description="Collect browser/system fingerprint")
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="User metadata")
    
    @validator('phone')
    def validate_phone_or_email(cls, v, values):
        if not v and not values.get('email'):
            raise ValueError('Either email or phone must be provided')
        return v
    
    @validator('phone')
    def validate_phone_format(cls, v):
        if v and not v.startswith('+'):
            raise ValueError('Phone must be in international format (+1234567890)')
        return v

class BatchLookupRequest(BaseModel):
    targets: List[str] = Field(..., min_items=1, max_items=10)
    advanced_analysis: bool = False
    priority: str = Field(default="normal", regex="^(low|normal|high|urgent)$")

# Response Schemas
class ProfileData(BaseModel):
    platform: PlatformType
    profile_url: str
    username: Optional[str]
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    company: Optional[str]
    job_title: Optional[str]
    profile_picture: Optional[str]
    last_activity: Optional[datetime]
    bio: Optional[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_verified: bool = False

class DeceptionIndicator(BaseModel):
    type: str
    confidence: float
    evidence: List[str]
    severity: str
    impact_score: float

class DeceptionAnalysis(BaseModel):
    overall_risk_score: float = Field(..., ge=0.0, le=1.0)
    deception_indicators: List[DeceptionIndicator]
    recommended_actions: List[str]
    confidence_level: str
    anomaly_count: int

class DigitalFootprint(BaseModel):
    browser_fingerprint: Dict[str, Any]
    system_profile: Dict[str, Any]
    network_characteristics: Dict[str, Any]
    hardware_profile: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]
    confidence_score: float
    risk_assessment: Dict[str, Any]
    unique_identifiers: List[str]

class LookupResponse(BaseModel):
    task_id: str
    status: TaskStatus
    email: Optional[str]
    phone: Optional[str]
    
    # Results
    profiles: List[ProfileData] = []
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    correlation_evidence: List[str] = []
    digital_footprint: Optional[DigitalFootprint] = None
    deception_analysis: Optional[DeceptionAnalysis] = None
    behavioral_analysis: Optional[Dict[str, Any]] = None
    
    # Metadata
    processing_time: Optional[float]
    platforms_searched: List[PlatformType] = []
    platforms_found: List[PlatformType] = []
    
    # Timestamps
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    progress: float = Field(0.0, ge=0.0, le=1.0)
    estimated_completion: Optional[datetime]
    current_phase: Optional[str]
    error_message: Optional[str]

class SystemHealthResponse(BaseModel):
    status: str
    components: Dict[str, str]
    timestamp: datetime
    version: str
    uptime: float

class AgentStatusResponse(BaseModel):
    agent_id: str
    platform: PlatformType
    status: str
    success_rate: float
    avg_response_time: float
    last_activity: Optional[datetime]
    is_healthy: bool

# Internal Schemas
class AIDecision(BaseModel):
    primary_decision: Any
    confidence: float
    supporting_evidence: List[Any]
    dissenting_opinions: List[Any]
    quality_score: float
    decision_tree: Dict[str, Any]

class BunkerAnalysis(BaseModel):
    analysis_id: str
    target: str
    analysis_data: Dict[str, Any]
    timestamp: datetime
    patterns_detected: List[str]
    similarity_score: float
    cluster_assignment: int

# Authentication Schemas
class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=200)

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

# Configuration Schemas
class AgentConfigUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    rate_limit: Optional[int] = Field(None, ge=1, le=1000)
    timeout: Optional[int] = Field(None, ge=5, le=300)
    config_data: Optional[Dict[str, Any]] = None

class SystemConfig(BaseModel):
    max_concurrent_tasks: int = Field(default=10, ge=1, le=100)
    task_timeout: int = Field(default=300, ge=60, le=3600)
    enable_advanced_analysis: bool = True
    enable_fingerprinting: bool = True
    rate_limits: Dict[str, int] = Field(default={
        "lookup_per_hour": 2,
        "batch_lookup_per_day": 5,
        "api_requests_per_minute": 60
    })
