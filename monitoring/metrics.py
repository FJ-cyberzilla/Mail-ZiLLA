# monitoring/metrics.py
from prometheus_client import Counter, Gauge, Histogram

# Metrics definitions
SEARCH_REQUESTS = Counter(
    "search_requests_total", "Total search requests", ["platform", "status"]
)
SEARCH_DURATION = Histogram("search_duration_seconds", "Search request duration")
ACTIVE_AGENTS = Gauge("active_agents", "Number of active agents")
API_ERRORS = Counter("api_errors_total", "API errors by platform", ["platform"])


def record_search_metrics(platform: str, duration: float, success: bool):
    SEARCH_REQUESTS.labels(
        platform=platform, status="success" if success else "error"
    ).inc()
    SEARCH_DURATION.observe(duration)
