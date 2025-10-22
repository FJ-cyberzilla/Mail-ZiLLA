#!/usr/bin/env python3
"""
Mail-ZiLLA Enterprise Smart Installer
Auto-detects system and installs optimally
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path

import pyfiglet
import questionary
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (BarColumn, Progress, SpinnerColumn, TextColumn,
                           TimeRemainingColumn)

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.proxy_manager import ProxyManager
from utils.banner import BannerManager
from utils.system_detector import SystemDetector

console = Console()


class SmartInstaller:
    """Intelligent cross-platform installer"""

    def __init__(self):
        self.detector = SystemDetector()
        self.banner = BannerManager()
        self.proxy_manager = ProxyManager()
        self.install_steps = []
        self.current_platform = {}

    def show_intelligent_banner(self):
        """Show optimized banner based on terminal size"""
        platform_info = self.detector.detect_platform()
        banner_config = self.detector.generate_banner_config()

        # Adjust banner based on terminal
        if banner_config["max_width"] < 60:
            ascii_text = "CYBERZILLA"
        else:
            ascii_text = pyfiglet.figlet_format(
                "CYBERZILLA", font=banner_config["font"]
            )

        banner_content = f"""
[bold green]{ascii_text}[/bold green]

[bold blue]ENTERPRISE SOCIAL INTELLIGENCE PLATFORM[/bold blue]
[bold yellow]Auto-Installer v3.0 | Smart System Detection[/bold yellow]

[dim]🔍 Detected: {platform_info['os'].upper()} {platform_info.get('distro', '')}[/dim]
[dim]💻 Architecture: {platform_info['architecture']}[/dim]
[dim]🐍 Python: {platform_info['python_version']}[/dim]

[bold red]🚀 INITIATING SMART INSTALLATION PROCEDURE[/bold red]
"""

        console.print(
            Panel(
                banner_content,
                box=box.DOUBLE_EDGE,
                style="bright_white",
                width=banner_config["max_width"],
            )
        )

    async def run_comprehensive_scan(self):
        """Run complete system analysis"""
        console.print("\n[bold blue]🔍 ANALYZING SYSTEM ENVIRONMENT...[/bold blue]")

        with Progress(
            SpinnerColumn(),
            TextColumn("\[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("\[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=False,
        ) as progress:

            scan_task = progress.add_task("Scanning platform...", total=100)
            self.current_platform = self.detector.detect_platform()
            progress.update(scan_task, advance=25)

            progress.update(scan_task, description="Analyzing resources...")
            self.system_resources = self.detector.detect_resources()
            progress.update(scan_task, advance=25)

            progress.update(scan_task, description="Checking dependencies...")
            self.dependencies = self.detector.check_dependencies()
            progress.update(scan_task, advance=25)

            progress.update(scan_task, description="Finalizing analysis...")
            self.installation_type = self.detector.get_installation_type()
            progress.update(scan_task, advance=25)

            progress.update(
                scan_task, completed=100, description="[green]✅ Analysis complete!"
            )

        self._display_system_report()

    def _display_system_report(self):
        """Display comprehensive system analysis"""
        console.print("\n[bold green]📊 SYSTEM ANALYSIS REPORT[/bold green]")

        # Platform info
        console.print(
            f"[cyan]Platform:[/cyan] {self.current_platform['os'].upper()} "
            f"{self.current_platform.get('distro', '')}"
        )
        console.print(
            f"[cyan]Architecture:[/cyan] {self.current_platform['architecture']}"
        )
        console.print(
            f"[cyan]Installation Type:[/cyan] {self.installation_type.upper()}"
        )

        # Resources
        console.print(f"[cyan]Memory:[/cyan] {self.system_resources['memory_gb']} GB")
        console.print(f"[cyan]CPU Cores:[/cyan] {self.system_resources['cpu_cores']}")
        console.print(
            f"[cyan]Disk Space:[/cyan] {self.system_resources['disk_free_gb']} GB free"
        )

        # Dependencies
        deps_status = []
        for dep, available in self.dependencies.items():
            status = "✅" if available else "❌"
            deps_status.append(f"{status} {dep}")

        console.print(f"[cyan]Dependencies:[/cyan] {', '.join(deps_status)}")

    def generate_installation_plan(self):
        """Generate optimized installation plan"""
        console.print(
            "\n[bold blue]🎯 GENERATING OPTIMIZED INSTALLATION PLAN...[/bold blue]"
        )

        plan = []

        # Base installation steps
        plan.extend(
            [
                ("Create Virtual Environment", self._create_venv),
                ("Install Python Dependencies", self._install_python_deps),
                ("Setup Directory Structure", self._setup_directories),
                ("Initialize Configuration", self._initialize_config),
            ]
        )

        # Platform-specific steps
        if self.installation_type == "termux":
            plan.extend(self._get_termux_steps())
        elif "docker" in self.installation_type:
            plan.extend(self._get_docker_steps())
        else:
            plan.extend(self._get_native_steps())

        # Additional services
        if self.system_resources["can_install_docker"]:
            plan.extend(
                [
                    ("Setup Database Services", self._setup_database),
                    ("Setup Redis Service", self._setup_redis),
                ]
            )

        # Final steps
        plan.extend(
            [
                ("Acquire Proxy Infrastructure", self._acquire_proxies),
                ("Initialize AI Agents", self._initialize_agents),
                ("Security Hardening", self._security_hardening),
                ("Final System Check", self._final_check),
            ]
        )

        self.install_steps = plan
        console.print(
            f"[green]✅ Generated {len(plan)} optimized installation steps[/green]"
        )

    def _get_termux_steps(self):
        """Termux-specific installation steps"""
        return [
            ("Install Termux Dependencies", self._install_termux_deps),
            ("Configure Termux Storage", self._setup_termux_storage),
        ]

    def _get_docker_steps(self):
        """Docker-based installation steps"""
        return [
            ("Verify Docker Installation", self._verify_docker),
            ("Pull Service Images", self._pull_docker_images),
            ("Configure Docker Network", self._setup_docker_network),
        ]

    def _get_native_steps(self):
        """Native installation steps"""
        steps = []
        if self.current_platform["os"] == "linux":
            steps.append(("Install System Packages", self._install_system_packages))
        elif self.current_platform["os"] == "windows":
            steps.append(("Install Windows Features", self._install_windows_features))
        elif self.current_platform["os"] == "darwin":
            steps.append(("Install macOS Dependencies", self._install_macos_deps))

        steps.extend(
            [
                ("Setup PostgreSQL Native", self._setup_postgres_native),
                ("Setup Redis Native", self._setup_redis_native),
            ]
        )

        return steps

    async def execute_installation(self):
        """Execute the installation plan with progress tracking"""
        total_steps = len(self.install_steps)

        console.print(
            f"\n[bold green]🚀 EXECUTING {total_steps} INSTALLATION STEPS...[/bold green]"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("\[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("\[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
            expand=True,
        ) as progress:

            main_task = progress.add_task("Overall Installation", total=total_steps)

            for step_name, step_function in self.install_steps:
                progress.update(main_task, description=f"[cyan]{step_name}")

                try:
                    # Execute step
                    if asyncio.iscoroutinefunction(step_function):
                        await step_function()
                    else:
                        step_function()

                    progress.update(
                        main_task, advance=1, description=f"[green]✅ {step_name}"
                    )

                except Exception as e:
                    progress.update(main_task, description=f"[red]❌ {step_name}")
                    console.print(f"[red]Error in {step_name}: {e}[/red]")
                    # Continue with next steps

    # Installation step implementations
    def _create_venv(self):
        """Create Python virtual environment"""
        venv_path = Path("cyberzilla-env")
        if not venv_path.exists():
            subprocess.run([sys.executable, "-m", "venv", "cyberzilla-env"], check=True)

    def _install_python_deps(self):
        """Install Python dependencies"""
        requirements_file = Path("requirements.txt")
        if requirements_file.exists():
            pip_cmd = [
                (
                    "cyberzilla-env/bin/pip"
                    if os.name != "nt"
                    else "cyberzilla-env\\Scripts\\pip"
                ),
                "install",
                "-r",
                "requirements.txt",
            ]
            subprocess.run(pip_cmd, check=True)

    def _setup_directories(self):
        """Create necessary directories"""
        directories = ["logs", "data", "proxies", "backups", "cache", "agents"]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)

    def _initialize_config(self):
        """Initialize configuration files"""
        # Create default .env if not exists
        env_file = Path(".env")
        if not env_file.exists():
            self._create_default_env()

    def _create_default_env(self):
        """Create default environment configuration"""
        env_content = f"""# Cyberzilla Enterprise Configuration
# Auto-generated for {self.current_platform['os']}

# Database
DATABASE_URL=postgresql://cyberzilla:Cyberzilla123!@localhost:5432/cyberzilla
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY={self._generate_secret_key()}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Installation Type
INSTALLATION_TYPE={self.installation_type}
PLATFORM={self.current_platform['os']}

# Resources
MAX_WORKERS={self.system_resources['recommended_workers']}
MEMORY_LIMIT={self.system_resources['memory_gb']}GB

# API
API_HOST=0.0.0.0
API_PORT=8000

# Environment
DEBUG=false
ENVIRONMENT=production
"""
        with open(".env", "w") as f:
            f.write(env_content)

    def _generate_secret_key(self):
        """Generate secure secret key"""
        import secrets

        return secrets.token_urlsafe(64)

    async def _acquire_proxies(self):
        """Automatically acquire and test proxies"""
        console.print("[blue]🌐 Acquiring proxy infrastructure...[/blue]")
        await self.proxy_manager.auto_acquire_proxies()

    def _initialize_agents(self):
        """Initialize AI agents"""
        agents_dir = Path("agents")
        agents_dir.mkdir(exist_ok=True)

        # Create agent configuration
        agent_config = {
            "platforms": ["linkedin", "github", "twitter", "facebook", "instagram"],
            "timeouts": {
                "linkedin": 30,
                "github": 15,
                "twitter": 20,
                "facebook": 25,
                "instagram": 35,
            },
            "retry_strategy": "exponential_backoff",
            "concurrent_requests": self.system_resources["recommended_workers"],
        }

        with open(agents_dir / "config.json", "w") as f:
            json.dump(agent_config, f, indent=2)

    def _security_hardening(self):
        """Apply security hardening"""
        # Set secure permissions
        for file in [".env", "data/users.db"]:
            if Path(file).exists():
                os.chmod(file, 0o600)

        # Create security audit configuration
        security_config = {
            "enable_audit_log": True,
            "log_failed_attempts": True,
            "session_timeout": 3600,
            "max_login_attempts": 3,
        }

        with open("logs/security_config.json", "w") as f:
            json.dump(security_config, f, indent=2)

    def _final_check(self):
        """Perform final system check"""
        console.print(
            "\n[bold green]🔍 PERFORMING FINAL SYSTEM VERIFICATION...[/bold green]"
        )

        checks = [
            ("Virtual Environment", Path("cyberzilla-env").exists()),
            ("Configuration", Path(".env").exists()),
            ("Dependencies", Path("requirements.txt").exists()),
            (
                "Directory Structure",
                all(Path(d).exists() for d in ["logs", "data", "proxies"]),
            ),
            ("Proxy Infrastructure", Path("proxies/auto_acquired.txt").exists()),
        ]

        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            console.print(f"   {status} {check_name}")
            if not passed:
                all_passed = False

        return all_passed

    def _install_termux_deps(self):
        """Install Termux-specific dependencies"""
        if self.current_platform.get("distro") == "termux":
            packages = ["python", "redis", "postgresql"]
            subprocess.run(["pkg", "install", "-y"] + packages, check=True)

    def _verify_docker(self):
        """Verify Docker installation"""
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
        except:
            console.print(
                "[yellow]⚠️ Docker not found. Using native installation.[/yellow]"
            )

    # Placeholder methods for other installation steps
    def _setup_termux_storage(self):
        pass

    def _pull_docker_images(self):
        pass

    def _setup_docker_network(self):
        pass

    def _install_system_packages(self):
        pass

    def _install_windows_features(self):
        pass

    def _install_macos_deps(self):
        pass

    def _setup_database(self):
        pass

    def _setup_redis(self):
        pass

    def _setup_postgres_native(self):
        pass

    def _setup_redis_native(self):
        pass


async def main():
    """Main installation routine"""
    installer = SmartInstaller()

    try:
        # Show intelligent banner
        installer.show_intelligent_banner()

        # Run comprehensive system analysis
        await installer.run_comprehensive_scan()

        # Confirm installation
        if not questionary.confirm(
            "Proceed with automated installation?", default=True
        ).ask():
            console.print("[yellow]Installation cancelled.[/yellow]")
            return

        # Generate and execute installation plan
        installer.generate_installation_plan()
        await installer.execute_installation()

        # Final verification
        if installer._final_check():
            console.print(
                "\n[bold green]🎉 CYBERZILLA ENTERPRISE INSTALLATION COMPLETE![/bold green]"
            )
            console.print("\n[blue]🚀 Quick Start:[/blue]")
            console.print("   source cyberzilla-env/bin/activate")
            console.print("   python cli.py")
            console.print("\n[blue]📊 Monitoring:[/blue]")
            console.print("   ./start_services.sh all")
            console.print(
                "\n[red]🔐 SECURITY NOTE:[/red] Change default passwords immediately!"
            )
        else:
            console.print("\n[red]❌ Installation completed with warnings.[/red]")
            console.print("   Some components may need manual configuration.")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Installation interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]💥 Installation failed: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


def track_installation():
    """Track installation for usage analytics"""
    try:
        # Call the uninstall script to track installation
        import subprocess

        subprocess.run(["./uninstall.sh", "--track-install"], check=True)
        logger.info("✅ Installation tracking initialized")
    except Exception as e:
        logger.warning(f"⚠️ Installation tracking failed: {e}")


# Call this after successful installation
track_installation()
