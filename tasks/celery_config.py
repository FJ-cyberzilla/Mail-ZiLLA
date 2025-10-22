"""
CELERY CONFIGURATION - Enterprise Task Queue Setup
Advanced broker configuration, rate limiting, and task management
"""

import os
from datetime import timedelta

from celery import Celery
from kombu import Exchange, Queue

# Celery App Configuration
app = Celery("cyberzilla_enterprise")

# Broker and Backend Settings
app.conf.update(
    # Redis Broker Configuration
    broker_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    result_backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    # Serialization
    accept_content=["json", "pickle"],
    task_serializer="pickle",
    result_serializer="pickle",
    # Task Configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    # Queue Configuration
    task_default_queue="default",
    task_queues=(
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
        Queue("social_lookup", Exchange("social_lookup"), routing_key="social_lookup"),
        Queue(
            "proxy_management",
            Exchange("proxy_management"),
            routing_key="proxy_management",
        ),
        Queue("ai_analysis", Exchange("ai_analysis"), routing_key="ai_analysis"),
    ),
    # Rate Limiting
    task_annotations={
        "tasks.social_lookup_task": {"rate_limit": "2/h"},  # 2 per hour as specified
        "tasks.proxy_health_check": {"rate_limit": "10/m"},
        "tasks.ai_analysis_task": {"rate_limit": "5/m"},
    },
    # Retry Configuration
    task_default_retry_delay=30,  # 30 seconds
    task_max_retries=3,
    task_retry_backoff=True,
    task_retry_backoff_max=600,  # 10 minutes
    # Worker Configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    # Result Configuration
    result_expires=timedelta(hours=24),
    result_compression="gzip",
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    # Security
    worker_direct=True,  # Bypass broker for some operations
    broker_connection_retry_on_startup=True,
    # Timeouts
    broker_connection_timeout=30,
    broker_connection_retry=True,
    broker_connection_max_retries=3,
    # Task Routes
    task_routes={
        "tasks.social_lookup_task": {"queue": "social_lookup"},
        "tasks.proxy_health_check": {"queue": "proxy_management"},
        "tasks.ai_analysis_task": {"queue": "ai_analysis"},
        "tasks.urgent_analysis": {"queue": "high_priority"},
    },
)

# Beat Schedule for Periodic Tasks
app.conf.beat_schedule = {
    # Proxy Management
    "proxy-health-check": {
        "task": "tasks.proxy_health_check",
        "schedule": timedelta(minutes=5),
        "options": {"queue": "proxy_management"},
    },
    "proxy-refresh": {
        "task": "tasks.refresh_proxy_pool",
        "schedule": timedelta(hours=1),
        "options": {"queue": "proxy_management"},
    },
    # System Health
    "system-health-check": {
        "task": "tasks.system_health_check",
        "schedule": timedelta(minutes=10),
        "options": {"queue": "default"},
    },
    # AI Agent Maintenance
    "ai-agent-calibration": {
        "task": "tasks.calibrate_ai_agents",
        "schedule": timedelta(hours=6),
        "options": {"queue": "ai_analysis"},
    },
    # Data Cleanup
    "cleanup-old-tasks": {
        "task": "tasks.cleanup_old_task_results",
        "schedule": timedelta(hours=24),
        "options": {"queue": "default"},
    },
    # Bunker Analysis
    "bunker-pattern-analysis": {
        "task": "tasks.analyze_bunker_patterns",
        "schedule": timedelta(hours=12),
        "options": {"queue": "ai_analysis"},
    },
}

# Task Error Handling Configuration
app.conf.task_compression = "gzip"
app.conf.worker_cancel_long_running_tasks_on_connection_loss = True
app.conf.worker_enable_remote_control = True

if __name__ == "__main__":
    app.start()
