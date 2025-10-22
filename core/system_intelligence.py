"""
System and Hardware Intelligence Gathering
"""


class SystemIntelligence:
    async def gather_system_info(self) -> Dict[str, Any]:
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "hardware_concurrency": await self._get_cpu_cores(),
            "device_memory": await self._get_device_memory(),
            "screen_resolution": await self._get_screen_info(),
            "timezone": await self._get_timezone_info(),
            "language": await self._get_language_info(),
        }
