# monitoring/metrics.py
from prometheus_client import Counter, Gauge, Histogram

# Define metrics for monitoring
TASKS_PROCESSED = Counter("cyberzilla_tasks_processed", "Total tasks processed")
TASK_DURATION = Histogram("cyberzilla_task_duration", "Task processing duration")
ACTIVE_AGENTS = Gauge("cyberzilla_active_agents", "Number of active agents")