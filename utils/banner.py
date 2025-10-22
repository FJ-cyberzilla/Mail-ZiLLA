"""
ASCII Banner Management
Enterprise-grade banner display with security features
"""

from datetime import datetime

import pyfiglet
from rich import box
from rich.console import Console
from rich.panel import Panel


class BannerManager:
    """Manage secure banner display"""

    def __init__(self):
        self.console = Console()
        self.banners = {
            "main": self._create_main_banner,
            "security": self._create_security_banner,
            "success": self._create_success_banner,
            "warning": self._create_warning_banner,
            "error": self._create_error_banner,
        }

    def _create_main_banner(self, username: str = "Unknown") -> Panel:
        """Create main application banner"""
        ascii_banner = pyfiglet.figlet_format("CYBERZILLA", font="slant")

        banner_content = f"""
[bold green]{ascii_banner}[/bold green]

[bold blue]SOCIAL INTELLIGENCE PLATFORM - ENTERPRISE EDITION[/bold blue]
[bold yellow]Version 2.1.0 | Secure AI-Powered Lookup[/bold yellow]

[dim]🔐 Authenticated as: {username}[/dim]
[dim]🕐 Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]
[dim]🌐 GitHub: FJ-cyberzilla | Contact: cyberzilla.systems@gmail.com[/dim]

[bold red]🚨 WARNING: Authorized Use Only - All activities are logged[/bold red]
"""

        return Panel(
            banner_content,
            box=box.DOUBLE_EDGE,
            style="bright_white",
            title="🦖 CYBERZILLA ENTERPRISE",
            title_align="center",
        )

    def _create_security_banner(self, message: str) -> Panel:
        """Create security alert banner"""
        return Panel(
            f"[bold red]🔒 SECURITY ALERT[/bold red]\n\n{message}",
            box=box.DOUBLE_EDGE,
            style="red",
            title="🛡️ SECURITY NOTICE",
        )

    def _create_success_banner(self, message: str) -> Panel:
        """Create success banner"""
        return Panel(
            f"[bold green]✅ SUCCESS[/bold green]\n\n{message}",
            box=box.ROUNDED,
            style="green",
        )

    def _create_warning_banner(self, message: str) -> Panel:
        """Create warning banner"""
        return Panel(
            f"[bold yellow]⚠️ WARNING[/bold yellow]\n\n{message}",
            box=box.ROUNDED,
            style="yellow",
        )

    def _create_error_banner(self, message: str) -> Panel:
        """Create error banner"""
        return Panel(
            f"[bold red]💥 ERROR[/bold red]\n\n{message}", box=box.ROUNDED, style="red"
        )

    def display_banner(self, banner_type: str = "main", **kwargs):
        """Display specified banner type"""
        if banner_type in self.banners:
            banner = self.banners[banner_type](**kwargs)
            self.console.print(banner)
        else:
            self.console.print(f"[red]Unknown banner type: {banner_type}[/red]")

    def display_secure_launch(self):
        """Display secure launch sequence"""
        self.console.print("\n" + "=" * 60)
        self.display_banner("main", username="SYSTEM")
        self.console.print(
            "\n[bold green]🔒 Initializing secure environment...[/bold green]"
        )

        # Simulate security checks
        checks = [
            ("Security Protocols", "✅"),
            ("Crypto Libraries", "✅"),
            ("Access Controls", "✅"),
            ("Audit System", "✅"),
            ("Network Security", "✅"),
        ]

        for check, status in checks:
            self.console.print(f"   [cyan]{check}:[/cyan] {status}")
            import time

            time.sleep(0.2)

        self.console.print(
            "\n[bold green]🚀 Secure environment initialized![/bold green]"
        )
        self.console.print("=" * 60 + "\n")
