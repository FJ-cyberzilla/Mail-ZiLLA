import logging
from typing import Dict


class AlertManager:
    """Manages real-time alerting for system issues."""

    def __init__(self):
        self.logger = logging.getLogger("alert_manager")
        self.alert_history: Dict[str, int] = {}  # Stores count of active alerts

    async def trigger_alert(
        self,
        alert_name: str,
        severity: str,
        message: str,
        context: Dict = None,
        deduplication_key: str = None,
    ):
        """
        Triggers an alert. In a real system, this would integrate with PagerDuty, Slack, email, etc.
        For now, it logs the alert at the appropriate severity level.
        """
        log_method = getattr(self.logger, severity.lower(), self.logger.error)
        log_method(
            f"ALERT! [{alert_name}] - Severity: {severity} - Message: {message}",
            extra={"context": context, "deduplication_key": deduplication_key},
        )

        # Basic deduplication logic (can be expanded)
        if deduplication_key:
            self.alert_history[deduplication_key] = self.alert_history.get(deduplication_key, 0) + 1
            if self.alert_history[deduplication_key] > 5:  # Example: After 5 repeats, consider suppressing or escalating
                self.logger.warning(f"Repeated alert: {deduplication_key}. Consider escalation or suppression.")
        
    async def resolve_alert(self, deduplication_key: str):
        """Resolves an active alert."""
        if deduplication_key in self.alert_history:
            del self.alert_history[deduplication_key]
            self.logger.info(f"ALERT RESOLVED: {deduplication_key}")

    async def get_active_alerts(self) -> Dict[str, int]:
        """Returns a dictionary of currently active alerts."""
        return self.alert_history