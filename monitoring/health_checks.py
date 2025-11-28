import asyncio
import logging
from typing import Dict, List

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import get_settings


class HealthMonitor:
    """Monitors the health of various system components."""

    def __init__(self):
        self.logger = logging.getLogger("health_monitor")
        self.settings = get_settings()
        self.db_engine = None  # Initialized during health check
        self.redis_client = None  # Initialized during health check

    async def _get_db_engine(self):
        """Lazily initialize and return the async DB engine."""
        if self.db_engine is None:
            self.db_engine = create_async_engine(self.settings.database_url, echo=False)
        return self.db_engine

    async def _get_redis_client(self):
        """Lazily initialize and return the async Redis client."""
        if self.redis_client is None:
            self.redis_client = redis.from_url(
                self.settings.redis_url, password=self.settings.redis_password
            )
        return self.redis_client

    async def check_database_connection(self) -> Dict:
        """Checks the database connection."""
        try:
            engine = await self._get_db_engine()
            async_session = sessionmaker(
                engine, expire_on_commit=False, class_=AsyncSession
            )
            async with async_session() as session:
                await session.execute("SELECT 1")
            return {"status": "ok", "message": "Database connection successful."}
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return {"status": "error", "message": f"Database connection failed: {e}"}

    async def check_redis_connection(self) -> Dict:
        """Checks the Redis connection."""
        try:
            redis_client = await self._get_redis_client()
            await redis_client.ping()
            return {"status": "ok", "message": "Redis connection successful."}
        except Exception as e:
            self.logger.error(f"Redis health check failed: {e}")
            return {"status": "error", "message": f"Redis connection failed: {e}"}

    async def run_all_checks(self) -> Dict:
        """Runs all defined health checks."""
        results = await asyncio.gather(
            self.check_database_connection(),
            self.check_redis_connection(),
            return_exceptions=True  # Ensure all checks run even if one fails
        )

        overall_status = "ok"
        check_details = {}
        for i, res in enumerate(results):
            check_name = ["database", "redis"][i]
            if isinstance(res, Exception):
                overall_status = "error"
                check_details[check_name] = {"status": "error", "message": str(res)}
            else:
                if res["status"] == "error":
                    overall_status = "error"
                check_details[check_name] = res
        
        return {"status": overall_status, "checks": check_details}