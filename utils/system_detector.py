"""
Enterprise System Detection & Auto-Configuration
Intelligent platform detection and optimization
"""

import getpass
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import psutil


class SystemDetector:
    """Intelligent system detection and configuration"""

    def __init__(self):
        self.system_info = {}
        self.console = None

    def detect_platform(self) -> Dict[str, Any]:
        """Comprehensive platform detection"""
        system = platform.system().lower()
        architecture = platform.machine().lower()

        # Detect specific environments
        is_termux = "com.termux" in os.environ.get("PREFIX", "")
        is_wsl = "microsoft" in platform.uname().release.lower()
        is_docker = Path("/.dockerenv").exists()

        platform_info = {
            "os": system,
            "architecture": architecture,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "is_termux": is_termux,
            "is_wsl": is_wsl,
            "is_docker": is_docker,
            "hostname": socket.gethostname(),
            "username": getpass.getuser(),
        }

        # Detect specific OS variants
        if system == "linux":
            platform_info["distro"] = self._detect_linux_distro()
        elif system == "windows":
            platform_info["windows_version"] = platform.win32_ver()
        elif system == "darwin":
            platform_info["mac_version"] = platform.mac_ver()

        self.system_info = platform_info
        return platform_info

    def _detect_linux_distro(self) -> str:
        """Detect specific Linux distribution"""
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read()
                if "ubuntu" in content.lower():
                    return "ubuntu"
                elif "debian" in content.lower():
                    return "debian"
                elif "centos" in content.lower():
                    return "centos"
                elif "fedora" in content.lower():
                    return "fedora"
                elif "arch" in content.lower():
                    return "arch"
                elif "termux" in content.lower():
                    return "termux"
        except:
            pass
        return "linux"

    def get_terminal_size(self) -> Tuple[int, int]:
        """Get optimal terminal size with fallbacks"""
        try:
            columns, rows = shutil.get_terminal_size()
            # Ensure minimum usable size
            return max(columns, 80), max(rows, 24)
        except:
            return 80, 24  # Fallback size

    def detect_resources(self) -> Dict[str, Any]:
        """Detect system resources"""
        try:
            memory_gb = psutil.virtual_memory().total / (1024**3)
            cpu_cores = (
                psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True) or 1
            )
            disk_free = psutil.disk_usage(".").free / (1024**3)

            return {
                "memory_gb": round(memory_gb, 1),
                "cpu_cores": cpu_cores,
                "disk_free_gb": round(disk_free, 1),
                "can_install_docker": memory_gb >= 2 and disk_free >= 10,
                "recommended_workers": min(max(1, cpu_cores - 1), 8),
            }
        except:
            return {
                "memory_gb": 1.0,
                "cpu_cores": 1,
                "disk_free_gb": 5.0,
                "can_install_docker": False,
                "recommended_workers": 1,
            }

    def check_dependencies(self) -> Dict[str, bool]:
        """Check system dependencies"""
        deps = {
            "python_3_8": sys.version_info >= (3, 8),
            "pip": self._check_command("pip3") or self._check_command("pip"),
            "git": self._check_command("git"),
            "docker": self._check_command("docker"),
            "docker_compose": self._check_command("docker-compose"),
            "redis": self._check_command("redis-cli"),
            "postgresql": self._check_command("psql"),
        }

        # Platform-specific checks
        if self.system_info["os"] == "linux":
            deps["systemd"] = Path("/etc/systemd/system").exists()
            deps["apt"] = self._check_command("apt")  # Debian/Ubuntu
            deps["yum"] = self._check_command("yum")  # CentOS/RHEL
            deps["pacman"] = self._check_command("pacman")  # Arch

        return deps

    def _check_command(self, command: str) -> bool:
        """Check if command is available"""
        try:
            subprocess.run([command, "--version"], capture_output=True, timeout=5)
            return True
        except:
            return False

    def get_installation_type(self) -> str:
        """Determine optimal installation type"""
        if self.system_info["is_termux"]:
            return "termux"
        elif self.system_info.get("distro") in ["ubuntu", "debian", "centos"]:
            return "native_docker"
        elif self.system_info["os"] == "windows":
            return "windows_docker"
        elif self.system_info["os"] == "darwin":
            return "mac_docker"
        else:
            return "native_python"

    def generate_banner_config(self) -> Dict[str, Any]:
        """Generate optimal banner configuration for terminal"""
        width, height = self.get_terminal_size()

        # Adjust banner based on terminal size
        if width < 60:
            font = "small"
            max_width = 50
        elif width < 100:
            font = "standard"
            max_width = 80
        else:
            font = "slant"
            max_width = 120

        return {
            "font": font,
            "max_width": max_width,
            "terminal_width": width,
            "terminal_height": height,
            "use_unicode": self.system_info["os"]
            != "windows",  # Windows may have font issues
            "colors_enabled": "TERM" in os.environ
            and "color" in os.environ.get("TERM", ""),
        }
