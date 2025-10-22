#!/usr/bin/env python3
"""
Universal Cyberzilla Startup Script
Auto-detects platform and starts appropriate services
"""

import os
import sys
import platform
from pathlib import Path

def detect_platform():
    """Detect current platform"""
    system = platform.system().lower()
    is_termux = 'com.termux' in os.environ.get('PREFIX', '')
    return 'termux' if is_termux else system

def start_services():
    """Start services based on platform"""
    current_platform = detect_platform()
    
    print(f"🚀 Starting Cyberzilla on {current_platform.upper()}...")
    
    if current_platform == 'termux':
        # Termux-specific startup
        start_termux_services()
    elif current_platform == 'windows':
        # Windows-specific startup  
        start_windows_services()
    else:
        # Linux/macOS startup
        start_unix_services()

def start_termux_services():
    """Start services on Termux"""
    print("📱 Starting Termux-optimized services...")
    
    # Start services in background
    commands = [
        "source cyberzilla-env/bin/activate",
        "python cli.py"
    ]
    
    # For Termux, we can start directly
    os.system("source cyberzilla-env/bin/activate && python cli.py")

def start_windows_services():
    """Start services on Windows"""
    print("🪟 Starting Windows-optimized services...")
    
    # Use PowerShell or CMD based on availability
    venv_activate = "cyberzilla-env\\Scripts\\activate"
    if Path(venv_activate).exists():
        os.system(f"cmd /k \"{venv_activate} && python cli.py\"")
    else:
        os.system("python cli.py")

def start_unix_services():
    """Start services on Unix-like systems"""
    print("🐧 Starting Unix-optimized services...")
    
    # Check if we should start all services or just CLI
    if len(sys.argv) > 1 and sys.argv[1] == 'all':
        os.system("./start_services.sh all")
    else:
        os.system("source cyberzilla-env/bin/activate && python cli.py")

if __name__ == "__main__":
    start_services()
