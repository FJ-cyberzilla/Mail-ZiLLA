# monitoring/logging_config.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured JSON logging for production"""
    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    log_handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[log_handler]
    )

# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Define metrics for monitoring
TASKS_PROCESSED = Counter('cyberzilla_tasks_processed', 'Total tasks processed')
TASK_DURATION = Histogram('cyberzilla_task_duration', 'Task processing duration')
ACTIVE_AGENTS = Gauge('cyberzilla_active_agents', 'Number of active agents')
