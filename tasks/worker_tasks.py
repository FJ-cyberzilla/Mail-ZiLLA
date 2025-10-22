"""
CELERY WORKER TASKS - Enterprise Task Execution
Robust task execution with comprehensive error handling and retry logic
"""

from celery import Celery, current_task
import logging
from typing import Dict, Optional, Any
import asyncio
import time
from datetime import datetime
import traceback

from core.social_agent import social_agent
from core.validation import email_validator
from core.ai_hierarchy import AIHierarchyManager
from core.deception_detector import DeceptionDetector
from database.db import db_manager
from database.models import TaskResult
from core.schemas import LookupRequest, TaskStatus
from core.config import get_settings

app = Celery('cyberzilla_enterprise')
logger = logging.getLogger("worker_tasks")

@app.task(bind=True, name='tasks.social_lookup_task', max_retries=3, default_retry_delay=60)
def social_lookup_task(self, email: str, advanced_analysis: bool = False, user_context: Dict = None):
    """
    Main social lookup task with comprehensive error handling and retry logic
    """
    task_id = current_task.request.id
    start_time = time.time()
    
    logger.info(f"🎯 Starting social lookup task {task_id} for: {email}")
    
    try:
        # Update task status to processing
        _update_task_status(task_id, TaskStatus.PROCESSING, started_at=datetime.now())
        
        # Validate email before processing
        validation_result = asyncio.run(
            email_validator.validate_email_comprehensive(email)
        )
        
        if not validation_result['is_valid']:
            error_msg = f"Invalid email: {validation_result.get('details', {}).get('error', 'Unknown error')}"
            _update_task_status(task_id, TaskStatus.FAILED, error_message=error_msg)
            return {'error': error_msg, 'task_id': task_id}
        
        # Run the social lookup
        if advanced_analysis:
            result = asyncio.run(
                social_agent.process_email_enterprise(email, user_context)
            )
        else:
            result = asyncio.run(
                social_agent.process_email(email, user_context)
            )
        
        processing_time = time.time() - start_time
        
        # Store results in database
        _store_task_results(
            task_id=task_id,
            email=email,
            result=result,
            processing_time=processing_time,
            user_context=user_context
        )
        
        # Update task status to completed
        _update_task_status(
            task_id, 
            TaskStatus.COMPLETED, 
            completed_at=datetime.now(),
            processing_time=processing_time
        )
        
        logger.info(f"✅ Social lookup completed for {email} in {processing_time:.2f}s")
        
        return {
            'task_id': task_id,
            'status': 'completed',
            'confidence_score': getattr(result, 'confidence_score', 0),
            'profiles_found': len(getattr(result, 'profiles', [])),
            'processing_time': processing_time
        }
        
    except Exception as exc:
        processing_time = time.time() - start_time
        error_msg = f"Task failed: {str(exc)}"
        
        logger.error(f"❌ Social lookup failed for {email}: {error_msg}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        
        # Update task status to failed
        _update_task_status(
            task_id, 
            TaskStatus.FAILED, 
            error_message=error_msg,
            processing_time=processing_time
        )
        
        # Retry logic
        if self.request.retries < self.max_retries:
            retry_delay = self.default_retry_delay * (2 ** self.request.retries)  # Exponential backoff
            logger.info(f"🔄 Retrying task {task_id} in {retry_delay}s (attempt {self.request.retries + 1})")
            raise self.retry(exc=exc, countdown=retry_delay)
        else:
            logger.error(f"💥 Task {task_id} failed after {self.max_retries} retries")
            return {
                'task_id': task_id,
                'status': 'failed',
                'error': error_msg,
                'processing_time': processing_time
            }

@app.task(bind=True, name='tasks.batch_lookup_task', max_retries=2)
def batch_lookup_task(self, emails: list, user_context: Dict = None):
    """
    Batch email lookup task with individual error handling
    """
    task_id = current_task.request.id
    logger.info(f"🎯 Starting batch lookup task {task_id} for {len(emails)} emails")
    
    results = []
    failed_emails = []
    
    for email in emails:
        try:
            # Submit individual lookup tasks
            result = social_lookup_task.apply_async(
                args=[email, False, user_context],
                queue='social_lookup'
            )
            results.append({
                'email': email,
                'task_id': result.id,
                'status': 'submitted'
            })
            
        except Exception as e:
            logger.error(f"❌ Failed to submit task for {email}: {e}")
            failed_emails.append({
                'email': email,
                'error': str(e)
            })
    
    return {
        'batch_task_id': task_id,
        'submitted_tasks': len(results),
        'failed_submissions': len(failed_emails),
        'results': results,
        'failed_emails': failed_emails
    }

@app.task(name='tasks.urgent_analysis')
def urgent_analysis(email: str, user_context: Dict = None):
    """
    High-priority analysis with enhanced resources
    """
    task_id = current_task.request.id
    logger.info(f"🚨 Starting urgent analysis for: {email}")
    
    try:
        # Use enterprise-grade analysis with all features enabled
        result = asyncio.run(
            social_agent.process_email_enterprise(
                email, 
                user_context, 
                collect_fingerprint=True
            )
        )
        
        # Store with high-priority flag
        _store_task_results(
            task_id=task_id,
            email=email,
            result=result,
            processing_time=0,  # Will be calculated
            user_context=user_context,
            priority='urgent'
        )
        
        return {
            'task_id': task_id,
            'status': 'completed',
            'priority': 'urgent',
            'confidence_score': getattr(result, 'confidence_score', 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Urgent analysis failed for {email}: {e}")
        return {
            'task_id': task_id,
            'status': 'failed',
            'error': str(e)
        }

def _update_task_status(task_id: str, status: TaskStatus, **kwargs):
    """Update task status in database"""
    try:
        with db_manager.get_db() as db:
            task = db.query(TaskResult).filter(TaskResult.id == task_id).first()
            
            if not task:
                # Create new task record
                task = TaskResult(id=task_id)
                db.add(task)
            
            task.status = status.value
            
            if 'started_at' in kwargs:
                task.started_at = kwargs['started_at']
            if 'completed_at' in kwargs:
                task.completed_at = kwargs['completed_at']
            if 'error_message' in kwargs:
                task.error_message = kwargs['error_message']
            if 'processing_time' in kwargs:
                task.processing_time = kwargs['processing_time']
            
            db.commit()
            
    except Exception as e:
        logger.error(f"Failed to update task status for {task_id}: {e}")

def _store_task_results(task_id: str, email: str, result: Any, processing_time: float, 
                       user_context: Dict = None, priority: str = 'normal'):
    """Store task results in database"""
    try:
        with db_manager.get_db() as db:
            task = db.query(TaskResult).filter(TaskResult.id == task_id).first()
            
            if not task:
                task = TaskResult(id=task_id)
                db.add(task)
            
            task.email = email
            task.status = 'completed'
            task.completed_at = datetime.now()
            task.processing_time = processing_time
            
            # Extract result data
            if hasattr(result, 'profiles'):
                task.profiles_found = [
                    {
                        'platform': p.platform,
                        'profile_url': p.profile_url,
                        'username': p.username,
                        'full_name': p.full_name,
                        'confidence': p.confidence
                    } for p in result.profiles
                ]
            
            if hasattr(result, 'confidence_score'):
                task.confidence_score = result.confidence_score
            
            if hasattr(result, 'correlation_evidence'):
                task.correlation_evidence = result.correlation_evidence
            
            if hasattr(result, 'digital_footprint'):
                task.digital_footprint = result.digital_footprint.__dict__
            
            if hasattr(result, 'deception_analysis'):
                task.deception_analysis = result.deception_analysis.__dict__
            
            # Platform coverage
            if hasattr(result, 'profiles'):
                platforms = list(set(p.platform for p in result.profiles))
                task.platform_coverage = platforms
            
            # Agent versions (would be populated from actual agent data)
            task.agent_versions = {'social_agent': '2.1.0'}
            
            db.commit()
            
    except Exception as e:
        logger.error(f"Failed to store task results for {task_id}: {e}")
