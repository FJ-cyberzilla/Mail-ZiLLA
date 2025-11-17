"""
API ROUTES - Enterprise endpoint definitions
Cyberzilla Enterprise Intelligence Platform v2.1.0
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException, Path,
                     Query)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.schemas import *
from core.validation import email_validator
from database.db import db_manager
from database.models import TaskResult
from security.input_sanitizer import sanitize_input
from security.rate_limiter import RateLimiter
from tasks.worker_tasks import (batch_lookup_task, social_lookup_task,
                                urgent_analysis)

router = APIRouter()
security = HTTPBearer()
rate_limiter = RateLimiter()
logger = logging.getLogger("api_routes")


# Dependency for authentication (simplified for example)
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify JWT token - in production, this would validate against your auth system
    """
    # This is a simplified example - implement proper JWT validation
    token = credentials.credentials
    if not token.startswith("eyJ"):  # Simple JWT format check
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"user_id": "example_user", "scope": "full_access"}


@router.post(
    "/lookup",
    response_model=LookupResponse,
    summary="Social Intelligence Lookup",
    description="""
    Perform comprehensive social intelligence lookup by email or phone.
    
    This endpoint initiates a multi-platform search across 25+ social networks,
    messaging apps, and professional platforms to build a complete digital footprint.
    
    Features:
    * 🔍 Cross-platform profile discovery
    * 🎯 AI-powered correlation
    * 🕵️ Deception detection  
    * 📊 Digital footprint analysis
    * ⚡ Real-time processing
    
    Rate Limit: 2 requests per hour per user
    """,
)
async def social_lookup(
    request: LookupRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(verify_token),
):
    """
    Submit email or phone for social intelligence analysis
    """
    # Rate limiting
    user_id = current_user["user_id"]
    await rate_limiter.check_rate_limit(
        identifier=f"lookup_{user_id}", limit=2, window=3600  # 2 lookups per hour
    )

    # Input validation
    if not request.email and not request.phone:
        raise HTTPException(
            status_code=422, detail="Either email or phone must be provided"
        )

    if request.email:
        # Sanitize and validate email
        sanitized_email = sanitize_input(request.email)
        validation = await email_validator.validate_email_comprehensive(sanitized_email)

        if not validation["is_valid"]:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid email address: {validation.get('details', {}).get('error', 'Unknown error')}",
            )

        if validation["risk_score"] > 0.8:
            raise HTTPException(
                status_code=422,
                detail="High-risk email address detected - cannot process",
            )

    if request.phone:
        # Sanitize phone
        sanitized_phone = sanitize_input(request.phone)
        if not sanitized_phone.startswith("+"):
            raise HTTPException(
                status_code=422,
                detail="Phone must be in international format (+1234567890)",
            )

    # Submit to Celery task queue
    try:
        task = social_lookup_task.delay(
            email=request.email,
            phone=request.phone,
            advanced_analysis=request.advanced_analysis,
            collect_fingerprint=request.collect_fingerprint,
            user_context={
                "user_id": user_id,
                "client_ip": "0.0.0.0",  # Would be real IP in production
                "request_timestamp": datetime.now().isoformat(),
            },
        )

        logger.info(f"Lookup task submitted: {task.id} for user {user_id}")

        return LookupResponse(
            task_id=task.id,
            status=TaskStatus.PENDING,
            email=request.email,
            phone=request.phone,
            created_at=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Failed to submit lookup task: {e}")
        raise HTTPException(status_code=500, detail="Failed to process lookup request")


@router.post(
    "/lookup/batch",
    response_model=BatchLookupResponse,
    summary="Batch Lookup",
    description="""
    Perform batch social intelligence lookup for multiple targets.
    
    Process up to 10 emails/phones in a single request with optimized
    resource usage and parallel processing.
    
    Rate Limit: 5 batch requests per day per user
    """,
)
async def batch_lookup(
    request: BatchLookupRequest, current_user: dict = Depends(verify_token)
):
    """
    Submit batch of emails/phones for analysis
    """
    # Rate limiting
    user_id = current_user["user_id"]
    await rate_limiter.check_rate_limit(
        identifier=f"batch_lookup_{user_id}",
        limit=5,  # 5 batch requests per day
        window=86400,
    )

    # Validate targets
    if len(request.targets) > 10:
        raise HTTPException(
            status_code=422, detail="Maximum 10 targets allowed per batch request"
        )

    validated_targets = []
    for target in request.targets:
        sanitized_target = sanitize_input(target)

        # Simple email/phone validation
        if "@" in sanitized_target:
            if not await email_validator.validate_format(sanitized_target):
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid email in batch: {sanitized_target}",
                )
        elif sanitized_target.startswith("+"):
            # Basic phone format check
            if len(sanitized_target) < 10:
                raise HTTPException(
                    status_code=422, detail=f"Invalid phone format: {sanitized_target}"
                )
        else:
            raise HTTPException(
                status_code=422, detail=f"Invalid target format: {sanitized_target}"
            )

        validated_targets.append(sanitized_target)

    # Submit batch task
    try:
        task = batch_lookup_task.delay(
            targets=validated_targets,
            user_context={"user_id": user_id, "priority": request.priority},
        )

        return BatchLookupResponse(
            batch_task_id=task.id,
            targets_count=len(validated_targets),
            status="submitted",
            submitted_at=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Failed to submit batch lookup: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to process batch lookup request"
        )


@router.get(
    "/lookup/{task_id}/status",
    response_model=TaskStatusResponse,
    summary="Get Task Status",
    description="Check the status of a social intelligence lookup task",
)
async def get_task_status(
    task_id: str = Path(..., description="The task ID to check"),
    current_user: dict = Depends(verify_token),
):
    """
    Get status of a specific lookup task
    """
    try:
        with db_manager.get_db() as db:
            task = db.query(TaskResult).filter(TaskResult.id == task_id).first()

            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            # Basic authorization check (in production, verify user owns task)

            # Calculate progress based on task state
            progress = 0.0
            current_phase = "unknown"

            if task.status == "completed":
                progress = 1.0
                current_phase = "completed"
            elif task.status == "processing":
                progress = 0.5
                current_phase = "analysis"
            elif task.status == "pending":
                progress = 0.1
                current_phase = "queued"

            return TaskStatusResponse(
                task_id=task_id,
                status=TaskStatus(task.status),
                progress=progress,
                current_phase=current_phase,
                started_at=task.started_at,
                error_message=task.error_message,
            )

    except Exception as e:
        sanitized_task_id = task_id.replace('\n', '').replace('\r', '')
        logger.error(f"Failed to get task status {sanitized_task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve task status")


@router.get(
    "/lookup/{task_id}/results",
    response_model=LookupResponse,
    summary="Get Task Results",
    description="Retrieve the results of a completed social intelligence lookup",
)
async def get_task_results(
    task_id: str = Path(..., description="The task ID to retrieve results for"),
    current_user: dict = Depends(verify_token),
):
    """
    Get results of a completed lookup task
    """
    try:
        with db_manager.get_db() as db:
            task = db.query(TaskResult).filter(TaskResult.id == task_id).first()

            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            if task.status != "completed":
                raise HTTPException(status_code=422, detail="Task not completed yet")

            # Convert database task to response schema
            return LookupResponse(
                task_id=task.id,
                status=TaskStatus(task.status),
                email=task.email,
                phone=task.phone,
                profiles=task.profiles_found or [],
                confidence_score=task.confidence_score or 0.0,
                correlation_evidence=task.correlation_evidence or [],
                digital_footprint=task.digital_footprint,
                deception_analysis=task.deception_analysis,
                behavioral_analysis=task.behavioral_analysis,
                processing_time=task.processing_time,
                platforms_searched=task.platform_coverage or [],
                platforms_found=list(
                    set(p["platform"] for p in (task.profiles_found or []))
                ),
                created_at=task.created_at,
                started_at=task.started_at,
                completed_at=task.completed_at,
            )

    except Exception as e:
        logger.error(f"Failed to get task results {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve task results")


@router.post(
    "/analysis/urgent",
    response_model=UrgentAnalysisResponse,
    summary="Urgent Analysis",
    description="""
    High-priority analysis with enhanced resources and faster processing.
    
    Uses dedicated resources and optimized algorithms for time-sensitive
    intelligence requirements.
    
    Rate Limit: 1 urgent analysis per hour per user
    """,
)
async def urgent_analysis_request(
    target: str = Query(..., description="Email or phone to analyze"),
    current_user: dict = Depends(verify_token),
):
    """
    Submit urgent analysis request
    """
    # Rate limiting
    user_id = current_user["user_id"]
    await rate_limiter.check_rate_limit(
        identifier=f"urgent_{user_id}",
        limit=1,  # 1 urgent request per hour
        window=3600,
    )

    # Validate target
    sanitized_target = sanitize_input(target)

    if "@" in sanitized_target:
        if not await email_validator.validate_format(sanitized_target):
            raise HTTPException(status_code=422, detail="Invalid email address")
    elif not sanitized_target.startswith("+"):
        raise HTTPException(
            status_code=422,
            detail="Phone must be in international format (+1234567890)",
        )

    # Submit urgent task
    try:
        task = urgent_analysis.delay(
            target=sanitized_target,
            user_context={"user_id": user_id, "priority": "urgent"},
        )

        return UrgentAnalysisResponse(
            task_id=task.id,
            target=sanitized_target,
            priority="urgent",
            estimated_completion=datetime.now() + timedelta(minutes=5),
            submitted_at=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Failed to submit urgent analysis: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to process urgent analysis request"
        )


@router.get(
    "/system/agents",
    response_model=List[AgentStatusResponse],
    summary="Get Agent Status",
    description="Retrieve status and performance metrics for all AI agents",
)
async def get_agent_status(current_user: dict = Depends(verify_token)):
    """
    Get status of all AI agents
    """
    try:
        from core.ai_hierarchy import ai_hierarchy

        performance_report = ai_hierarchy.get_agent_performance_report()
        agents_status = []

        for agent_id, details in performance_report.get("agent_details", {}).items():
            agents_status.append(
                AgentStatusResponse(
                    agent_id=agent_id,
                    platform=details.get("platform", "unknown"),
                    status=details.get("status", "unknown"),
                    success_rate=details.get("success_rate", 0),
                    avg_response_time=details.get("avg_response_time", 0),
                    last_activity=details.get("last_activity"),
                    is_healthy=details.get("performance_rating")
                    in ["excellent", "good"],
                )
            )

        return agents_status

    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agent status")


@router.get(
    "/system/performance",
    response_model=SystemPerformanceResponse,
    summary="System Performance",
    description="Get comprehensive system performance metrics and health status",
)
async def get_system_performance(current_user: dict = Depends(verify_token)):
    """
    Get system performance metrics
    """
    try:
        from core.ai_hierarchy import ai_hierarchy
        from core.resource_orchestrator import resource_orchestrator

        # Get resource performance
        resource_report = resource_orchestrator.get_performance_report()

        # Get agent performance
        agent_report = ai_hierarchy.get_agent_performance_report()

        # Get system health
        from api.main import app

        health_data = await app.routes[0].endpoint()  # Health check endpoint

        return SystemPerformanceResponse(
            system_health=health_data,
            resource_utilization=resource_report,
            agent_performance=agent_report,
            timestamp=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Failed to get system performance: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve system performance"
        )


@router.delete(
    "/lookup/{task_id}",
    summary="Cancel Task",
    description="Cancel a pending or processing lookup task",
)
async def cancel_task(
    task_id: str = Path(..., description="The task ID to cancel"),
    current_user: dict = Depends(verify_token),
):
    """
    Cancel a lookup task
    """
    try:
        with db_manager.get_db() as db:
            task = db.query(TaskResult).filter(TaskResult.id == task_id).first()

            if not task:
                raise HTTPException(status_code=404, detail="Task not found")

            # Only allow cancellation of pending/processing tasks
            if task.status not in ["pending", "processing"]:
                raise HTTPException(
                    status_code=422, detail="Cannot cancel completed or failed task"
                )

            # Update task status (in production, would also revoke Celery task)
            task.status = "cancelled"
            task.completed_at = datetime.now()
            db.commit()

            return {
                "task_id": task_id,
                "status": "cancelled",
                "cancelled_at": datetime.now(),
            }

    except Exception as e:
        safe_task_id = task_id.replace('\r', '').replace('\n', '')
        logger.error(f"Failed to cancel task {safe_task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel task")


# Additional response models needed for new endpoints
class BatchLookupResponse(BaseModel):
    batch_task_id: str
    targets_count: int
    status: str
    submitted_at: datetime


class UrgentAnalysisResponse(BaseModel):
    task_id: str
    target: str
    priority: str
    estimated_completion: datetime
    submitted_at: datetime


class SystemPerformanceResponse(BaseModel):
    system_health: Dict[str, Any]
    resource_utilization: Dict[str, Any]
    agent_performance: Dict[str, Any]
    timestamp: datetime
