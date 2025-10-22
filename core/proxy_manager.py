"""
Enterprise Proxy Management
Automatic proxy acquisition, validation, and rotation
"""

import asyncio
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

import aiohttp


class ProxyManager:
    """Automatic proxy management with multiple sources"""

    def __init__(self):
        self.settings = get_settings()
        self.proxy_sources = [
            self._free_proxy_list,
            self._proxyscrape_list,
            self._geonode_list,
            self._premium_providers,  # Would require API keys
        ]
        self.active_proxies = []
        self.proxy_health = {}
        self.last_refresh = None

    async def auto_acquire_proxies(self) -> List[str]:
        """Automatically acquire proxies from multiple sources"""
        console.print("[bold blue]🤖 Acquiring proxies automatically...[/bold blue]")

        all_proxies = []

        # Try multiple sources concurrently
        tasks = [source() for source in self.proxy_sources[:3]]  # First 3 are free
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_proxies.extend(result)

        # Remove duplicates
        unique_proxies = list(set(all_proxies))

        console.print(
            f"[green]✅ Acquired {len(unique_proxies)} potential proxies[/green]"
        )

        # Health check proxies
        healthy_proxies = await self.health_check_proxies(unique_proxies)

        # Save for future use
        self._save_proxy_list(healthy_proxies)

        return healthy_proxies

    async def _free_proxy_list(self) -> List[str]:
        """Get proxies from free-proxy-list.net"""
        try:
            url = "https://free-proxy-list.net/"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        # Simple extraction - in practice, use proper parsing
                        proxies = []
                        lines = text.split("\n")
                        for line in lines:
                            if ":" in line and "." in line and len(line) < 25:
                                if line.strip().count(".") == 3:
                                    proxies.append(f"http://{line.strip()}")
                        return proxies[:50]  # Limit
        except:
            pass
        return []

    async def _proxyscrape_list(self) -> List[str]:
        """Get proxies from ProxyScrape"""
        try:
            url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        proxies = [
                            f"http://{line.strip()}"
                            for line in text.split("\n")
                            if line.strip()
                        ]
                        return proxies[:50]
        except:
            pass
        return []

    async def _geonode_list(self) -> List[str]:
        """Get proxies from Geonode (free tier)"""
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        proxies = []
                        for proxy in data.get("data", []):
                            proxies.append(f"http://{proxy['ip']}:{proxy['port']}")
                        return proxies
        except:
            pass
        return []

    async def _premium_providers(self) -> List[str]:
        """Placeholder for premium proxy providers"""
        # This would integrate with paid services like:
        # - BrightData
        # - Oxylabs
        # - SmartProxy
        # etc.
        return []

    async def health_check_proxies(self, proxies: List[str]) -> List[str]:
        """Health check proxies with concurrent testing"""
        console.print("[yellow]🔍 Testing proxy health...[/yellow]")

        healthy_proxies = []
        test_url = "http://httpbin.org/ip"  # Test endpoint

        async def test_proxy(proxy: str) -> Tuple[str, bool]:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        test_url, proxy=proxy, timeout=10
                    ) as response:
                        if response.status == 200:
                            return proxy, True
            except:
                pass
            return proxy, False

        # Test all proxies concurrently
        tasks = [test_proxy(proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks)

        for proxy, is_healthy in results:
            if is_healthy:
                healthy_proxies.append(proxy)

        console.print(
            f"[green]✅ {len(healthy_proxies)}/{len(proxies)} proxies passed health check[/green]"
        )
        return healthy_proxies

    def _save_proxy_list(self, proxies: List[str]):
        """Save proxy list for future use"""
        proxy_dir = Path("proxies")
        proxy_dir.mkdir(exist_ok=True)

        with open(proxy_dir / "auto_acquired.txt", "w") as f:
            for proxy in proxies:
                f.write(f"{proxy}\n")

    def get_proxy(self) -> Optional[str]:
        """Get a random healthy proxy"""
        if not self.active_proxies:
            # Load from file or acquire new ones
            proxy_file = Path("proxies/auto_acquired.txt")
            if proxy_file.exists():
                with open(proxy_file, "r") as f:
                    self.active_proxies = [line.strip() for line in f if line.strip()]

            if not self.active_proxies:
                # Trigger auto-acquisition
                asyncio.run(self.auto_acquire_proxies())
                proxy_file = Path("proxies/auto_acquired.txt")
                if proxy_file.exists():
                    with open(proxy_file, "r") as f:
                        self.active_proxies = [
                            line.strip() for line in f if line.strip()
                        ]

        if self.active_proxies:
            return random.choice(self.active_proxies)
        return None

    async def refresh_proxies_auto(self):
        """Automatically refresh proxy pool"""
        if self.last_refresh and datetime.now() - self.last_refresh < timedelta(
            hours=1
        ):
            return

        console.print("[blue]🔄 Auto-refreshing proxy pool...[/blue]")
        await self.auto_acquire_proxies()
        self.last_refresh = datetime.now()
