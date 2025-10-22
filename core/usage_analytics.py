"""
Usage Analytics for Installation Tracking
"""

import json
import time
from datetime import datetime
from pathlib import Path


class UsageAnalytics:
    def __init__(self):
        self.install_log = Path.home() / ".cyberzilla" / "install_tracking.log"
        self.usage_log = Path.home() / ".cyberzilla" / "usage_analytics.log"

    def get_installation_duration(self) -> str:
        """Calculate how long Cyberzilla has been installed"""
        if not self.install_log.exists():
            return "Unknown"

        try:
            with open(self.install_log, "r") as f:
                for line in f:
                    if line.startswith("INSTALL_TIMESTAMP="):
                        install_time = int(line.split("=")[1].strip())
                        current_time = int(time.time())
                        duration_seconds = current_time - install_time

                        hours = duration_seconds // 3600
                        minutes = (duration_seconds % 3600) // 60

                        return f"{hours}h {minutes}m"
        except:
            pass

        return "Unknown"

    def log_usage(self, action: str, details: dict = None):
        """Log usage analytics"""
        self.usage_log.parent.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details or {},
            "installation_duration": self.get_installation_duration(),
        }

        with open(self.usage_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
