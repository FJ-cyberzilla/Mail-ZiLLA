"""
ERROR HANDLING - Comprehensive error management and recovery
"""

import logging
from typing import Dict

from monitoring.alerts import AlertManager
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenException


class ErrorHandler:
    """Enterprise error handling and recovery"""

    def __init__(self):
        self.logger = logging.getLogger("error_handler")
        self.error_counts: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.alert_manager = AlertManager() # Use the new AlertManager

    def _get_circuit_breaker(self, agent_name: str) -> CircuitBreaker:
        """Get or create a circuit breaker for a given agent."""
        if agent_name not in self.circuit_breakers:
            self.circuit_breakers[agent_name] = CircuitBreaker()
        return self.circuit_breakers[agent_name]

    async def handle_agent_error(
        self, agent_name: str, error: Exception, context: Dict = None
    ):
        """Handle agent-specific errors with recovery strategies"""
        error_key = f"agent_{agent_name}_{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

        # Log error with context
        self.logger.error(
            f"Agent {agent_name} error: {error}",
            extra={"context": context, "error_count": self.error_counts[error_key]},
        )

        circuit_breaker = self._get_circuit_breaker(agent_name)

        # Notify circuit breaker of failure
        circuit_breaker._on_failure()

        # Implement recovery strategies based on error type
        if isinstance(error, ConnectionError):
            await self._handle_connection_error(agent_name, circuit_breaker)
        elif isinstance(error, TimeoutError):
            await self._handle_timeout_error(agent_name, circuit_breaker)

        # Alert if error count exceeds threshold
        if self.error_counts[error_key] > 10:
            await self._trigger_alert(agent_name, error)

    async def _handle_connection_error(self, agent_name: str, circuit_breaker: CircuitBreaker):
        """Handle connection-related errors"""
        self.logger.warning(f"Connection error for agent {agent_name}. Circuit breaker state: {circuit_breaker.state}")
        if circuit_breaker.state == "OPEN":
            await self.alert_manager.trigger_alert(
                alert_name=f"{agent_name}_Connection_Circuit_Open",
                severity="CRITICAL",
                message=f"Agent {agent_name}'s circuit for connections is OPEN. All requests will fail.",
                deduplication_key=f"{agent_name}_connection_circuit_open"
            )
        # Further retry logic or proxy rotation could be implemented here

    async def _handle_timeout_error(self, agent_name: str, circuit_breaker: CircuitBreaker):
        """Handle timeout errors"""
        self.logger.warning(f"Timeout error for agent {agent_name}. Circuit breaker state: {circuit_breaker.state}")
        if circuit_breaker.state == "OPEN":
            await self.alert_manager.trigger_alert(
                alert_name=f"{agent_name}_Timeout_Circuit_Open",
                severity="CRITICAL",
                message=f"Agent {agent_name}'s circuit for timeouts is OPEN. All requests will fail.",
                deduplication_key=f"{agent_name}_timeout_circuit_open"
            )
        # Further adjustments to timeouts or concurrency could be implemented here

    async def _trigger_alert(self, agent_name: str, error: Exception):
        """Trigger alert for recurring errors"""
        self.logger.critical(
            f"CRITICAL: Agent {agent_name} has recurring errors: {error}"
        )
        await self.alert_manager.trigger_alert(
            alert_name=f"{agent_name}_Recurring_Errors",
            severity="CRITICAL",
            message=f"Agent {agent_name} is experiencing recurring errors: {error}",
            deduplication_key=f"{agent_name}_recurring_errors"
        )