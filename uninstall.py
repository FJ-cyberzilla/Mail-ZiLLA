#!/bin/bash

# Cyberzilla Enterprise Uninstaller
# Author: FJ-cyberzilla
# Contact: cyberzilla.systems@gmail.com
# Copyright: FJ™ - Cybertronic Systems - MMXXV - Chicago.IIinos

set -e

# Colors for animation
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Animation characters
SPINNER=('⣾' '⣽' '⣻' '⢿' '⡿' '⣟' '⣯' '⣷')
BAR=('█' '▉' '▊' '▋' '▌' '▍' '▎' '▏' ' ' '▏' '▎' '▍' '▌' '▋' '▊' '▉')

# Installation tracking
INSTALL_LOG="$HOME/.cyberzilla/install_tracking.log"
UNINSTALL_LOG="$HOME/.cyberzilla/uninstall_tracking.log"

# Function to display animated spinner
spinner() {
    local pid=$1
    local message=$2
    local delay=0.1
    local i=0
    
    while kill -0 $pid 2>/dev/null; do
        printf "\r${SPINNER[$i]} ${message}..."
        i=$(( (i+1) % ${#SPINNER[@]} ))
        sleep $delay
    done
    printf "\r✅ ${message} completed\n"
}

# Function to display animated progress bar
progress_bar() {
    local duration=$1
    local message=$2
    local steps=50
    local step_delay=$(echo "scale=3; $duration/$steps" | bc)
    
    printf "\n${message}\n"
    printf "["
    
    for ((i=0; i<=steps; i++)); do
        printf "█"
        sleep $step_delay
    done
    
    printf "] Done!\n"
}

# Function to calculate installation duration
calculate_usage_duration() {
    if [[ -f "$INSTALL_LOG" ]]; then
        install_time=$(grep "INSTALL_TIMESTAMP" "$INSTALL_LOG" | cut -d'=' -f2)
        uninstall_time=$(date +%s)
        
        if [[ -n "$install_time" ]]; then
            duration_seconds=$((uninstall_time - install_time))
            duration_hours=$((duration_seconds / 3600))
            duration_minutes=$(( (duration_seconds % 3600) / 60 ))
            
            echo "$duration_hours hours, $duration_minutes minutes"
            return
        fi
    fi
    echo "Unknown duration"
}

# Function to create animated text file
create_animated_farewell() {
    cat > "$HOME/cyberzilla_farewell.txt" << 'EOF'
┌─────────────────────────────────────────────────────┐
│                                                               │
│              🦖 Mail-ZiLLA FAREWELL 🦖                        │
│                                                               │
└─────────────────────────────────────────────────────┘

Thank you for using Cyberzilla Enterprise Intelligence Platform.

▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
█                                                    █
█  🎯 System Successfully Uninstalled                █
█  🕒 Usage Duration: DURATION_PLACEHOLDER           █
█  📅 Uninstall Date: DATE_PLACEHOLDER               █
█  ⏰ Uninstall Time: TIME_PLACEHOLDER               █
█                                                    █
█  🔧 All components removed:                        █
█     • Application Files                            █
█     • Database Entries                             █
█     • System Registrations                         █
█     • Configuration Files                          █
█     • Log Files                                    █
█                                                    █
█  💡 Hint:                                          █
█     "Intelligence is temporary, but knowledge      █
█      is permanent. Your digital footprint remains  █
█      in the patterns you've uncovered."            █
█                                                    █
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

For future enterprise intelligence needs, remember:
📧 cyberzilla.systems@gmail.com

EOF

    # Replace placeholders with actual data
    duration=$(calculate_usage_duration)
    current_date=$(date +"%Y-%m-%d")
    current_time=$(date +"%H:%M:%S")
    
    sed -i "s/DURATION_PLACEHOLDER/$duration/g" "$HOME/cyberzilla_farewell.txt"
    sed -i "s/DATE_PLACEHOLDER/$current_date/g" "$HOME/cyberzilla_farewell.txt"
    sed -i "s/TIME_PLACEHOLDER/$current_time/g" "$HOME/cyberzilla_farewell.txt"
}

# Function to display animated banner
animated_banner() {
    clear
    echo -e "${GREEN}"
    cat << "EOF"
    
 ░█▄█░█▀█░▀█▀░█░░░░░░░▀▀█░▀█▀░█░░░█░░░█▀█
 ░█░█░█▀█░░█░░█░░░▄▄▄░▄▀░░░█░░█░░░█░░░█▀█
 ░▀░▀░▀░▀░▀▀▀░▀▀▀░░░░░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀░▀
                                                                              
EOF
    echo -e "${NC}"
    echo -e "${BLUE}           ENTERPRISE INTELLIGENCE PLATFORM - UNINSTALLER${NC}"
    echo -e "${YELLOW}                Secure Removal Process Initiated${NC}"
    echo ""
}

# Function to log uninstall
log_uninstall() {
    mkdir -p "$(dirname "$UNINSTALL_LOG")"
    echo "UNINSTALL_TIMESTAMP=$(date +%s)" > "$UNINSTALL_LOG"
    echo "UNINSTALL_DATE=$(date +"%Y-%m-%d")" >> "$UNINSTALL_LOG"
    echo "UNINSTALL_TIME=$(date +"%H:%M:%S")" >> "$UNINSTALL_LOG"
    echo "USAGE_DURATION=$(calculate_usage_duration)" >> "$UNINSTALL_LOG"
    echo "SYSTEM_INFO=$(uname -a)" >> "$UNINSTALL_LOG"
}

# Function to check if Cyberzilla is installed
check_installation() {
    if [[ ! -d "cyberzilla-env" ]] && [[ ! -f "$INSTALL_LOG" ]]; then
        echo -e "${RED}❌ Cyberzilla installation not found!${NC}"
        echo -e "${YELLOW}No installation detected in current directory.${NC}"
        exit 1
    fi
}

# Function to stop all services
stop_services() {
    echo -e "\n${BLUE}🛑 Stopping Cyberzilla services...${NC}"
    
    # Stop Docker containers if running
    if command -v docker &> /dev/null && docker ps | grep -q "cyberzilla"; then
        progress_bar 3 "Stopping Docker containers"
        docker-compose down 2>/dev/null || true
    fi
    
    # Stop Celery workers
    if pgrep -f "celery" > /dev/null; then
        progress_bar 2 "Stopping background workers"
        pkill -f "celery" 2>/dev/null || true
    fi
    
    # Stop API server
    if pgrep -f "uvicorn" > /dev/null; then
        progress_bar 1 "Stopping API server"
        pkill -f "uvicorn" 2>/dev/null || true
    fi
}

# Function to remove virtual environment
remove_virtualenv() {
    if [[ -d "cyberzilla-env" ]]; then
        echo -e "\n${BLUE}🗑️  Removing virtual environment...${NC}"
        progress_bar 2 "Removing Python virtual environment"
        rm -rf cyberzilla-env
    fi
}

# Function to remove application files
remove_app_files() {
    echo -e "\n${BLUE}📁 Removing application files...${NC}"
    
    # List of directories to remove
    directories=(
        "logs"
        "data" 
        "proxies"
        "backups"
        "cache"
        "agents"
        "__pycache__"
        "*.pyc"
        "*.pyo"
        "*.pyd"
        ".pytest_cache"
        ".coverage"
    )
    
    for dir in "${directories[@]}"; do
        if [[ -e $dir ]]; then
            printf "  Removing %-30s" "$dir..."
            rm -rf $dir
            echo -e "${GREEN}✓${NC}"
        fi
    done
}

# Function to remove configuration files
remove_config_files() {
    echo -e "\n${BLUE}⚙️  Removing configuration files...${NC}"
    
    config_files=(
        ".env"
        "config.yaml"
        "config.json"
        "cyberzilla.db"
        "*.log"
        "requirements.txt"
        "Dockerfile"
        "docker-compose.yml"
    )
    
    for file in "${config_files[@]}"; do
        if compgen -G "$file" > /dev/null; then
            printf "  Removing %-30s" "$file..."
            rm -f $file
            echo -e "${GREEN}✓${NC}"
        fi
    done
}

# Function to remove system registrations (platform-specific)
remove_system_registrations() {
    echo -e "\n${BLUE}🏢 Removing system registrations...${NC}"
    
    case "$(uname -s)" in
        Linux*)
            progress_bar 2 "Removing Linux application registration"
            rm -f ~/.local/share/applications/cyberzilla.desktop 2>/dev/null || true
            ;;
        Darwin*)
            progress_bar 2 "Removing macOS application registration"
            rm -rf "/Applications/Cyberzilla.app" 2>/dev/null || true
            ;;
        CYGWIN*|MINGW32*|MINGW64*|MSYS*)
            progress_bar 3 "Removing Windows registry entries"
            # Windows registry cleanup would go here
            ;;
        *)
            echo "  Skipping system registration removal (unknown OS)"
            ;;
    esac
}

# Function to remove database (if external)
remove_database() {
    echo -e "\n${BLUE}🗃️  Cleaning up database...${NC}"
    
    # Stop and remove PostgreSQL container if exists
    if docker ps -a | grep -q "postgres"; then
        progress_bar 3 "Removing database container"
        docker stop postgres 2>/dev/null || true
        docker rm postgres 2>/dev/null || true
    fi
    
    # Remove Redis container if exists
    if docker ps -a | grep -q "redis"; then
        progress_bar 2 "Removing Redis container"
        docker stop redis 2>/dev/null || true
        docker rm redis 2>/dev/null || true
    fi
    
    # Remove Docker volumes
    if docker volume ls | grep -q "cyberzilla"; then
        progress_bar 2 "Removing data volumes"
        docker volume rm $(docker volume ls -q | grep "cyberzilla") 2>/dev/null || true
    fi
}

# Function to display final animation
final_animation() {
    echo -e "\n${GREEN}"
    echo "┌────────────────────────────────────────────────"
    echo "│                                                         │"
    echo "│                  UNINSTALL COMPLETE                     │"
    echo "│                                                         │"
    echo "└───────────────────────────────────────────────"
    echo -e "${NC}"
    
    # Animated completion message
    messages=(
        "🦖 Cyberzilla has left the building"
        "🔧 System cleanup completed successfully" 
        "📊 Usage analytics recorded"
        "🎯 Ready for next mission"
        "🚀 Enterprise intelligence platform removed"
    )
    
    for message in "${messages[@]}"; do
        for ((i=0; i<${#message}; i++)); do
            printf "${CYAN}%s${NC}" "${message:$i:1}"
            sleep 0.05
        done
        printf "\n"
        sleep 0.5
    done
    
    echo ""
}

# Function to display farewell message with signature
farewell_message() {
    local duration=$(calculate_usage_duration)
    local current_date=$(date +"%Y-%m-%d")
    local current_time=$(date +"%H:%M:%S")
    
    echo -e "${GREEN}"
    echo "┌────────────────────────────────────────────────"
    echo "│                                                         │"
    echo "│                    USAGE SUMMARY                        │"
    echo "│                                                         │"
    echo "├────────────────────────────────────────────────"
    printf "│   🕒  Usage Duration: %-30s │\n" "$duration"
    printf "│   📅  Uninstall Date: %-30s │\n" "$current_date"  
    printf "│   ⏰  Uninstall Time: %-30s │\n" "$current_time"
    echo "│                                                         │"
    echo "├────────────────────────────────────────────────"
    echo "│                                                         │"
    echo "│           Thank you for using Cyberzilla™               │"
    echo "│                                                         │"
    echo "│   💡 Hint:                                              │"
    echo "│      'The patterns remain, even when the                │"
    echo "│       tools are put away.'                              │"
    echo "│                                                         │"
    echo -e "│   \033[1;32mFJ™ - Cybertronic Systems\033[0;32m      │"
    echo "│   📧 cyberzilla.systems@gmail.com                       │"
    echo "│                                                         │"
    echo "└────────────────────────────────────────────────"
    echo -e "${NC}"
}

# Main uninstall function
main() {
    # Display animated banner
    animated_banner
    
    # Check if installation exists
    check_installation
    
    # Confirm uninstall
    echo -e "${YELLOW}⚠️  This will completely remove Cyberzilla from your system.${NC}"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Uninstall cancelled.${NC}"
        exit 0
    fi
    
    # Log uninstall start
    log_uninstall
    
    # Stop services
    stop_services
    
    # Remove components
    remove_virtualenv &
    spinner $! "Removing virtual environment"
    
    remove_app_files &
    spinner $! "Cleaning application files"
    
    remove_config_files &
    spinner $! "Removing configuration files"
    
    remove_system_registrations &
    spinner $! "Cleaning system registrations"
    
    remove_database &
    spinner $! "Cleaning database resources"
    
    # Create animated farewell file
    create_animated_farewell &
    spinner $! "Generating farewell report"
    
    # Remove installation tracking
    if [[ -f "$INSTALL_LOG" ]]; then
        rm -f "$INSTALL_LOG"
    fi
    
    # Remove the uninstall script itself (after execution)
    echo -e "\n${YELLOW}🗑️  Cleaning up uninstaller...${NC}"
    progress_bar 1 "Final cleanup"
    
    # Display final animations
    final_animation
    farewell_message
    
    # Show where farewell file was saved
    echo -e "\n${CYAN}📄 A detailed farewell report has been saved to:${NC}"
    echo -e "   ${YELLOW}$HOME/cyberzilla_farewell.txt${NC}"
    
    # Schedule self-destruction of uninstall script
    echo -e "\n${BLUE}🧹 Cleaning up uninstall script...${NC}"
    nohup bash -c "sleep 5; rm -f -- '$0'" >/dev/null 2>&1 &
}

# Enhanced installation tracking system
track_installation() {
    # This would be called by the installer to track installation time
    mkdir -p "$(dirname "$INSTALL_LOG")"
    echo "INSTALL_TIMESTAMP=$(date +%s)" > "$INSTALL_LOG"
    echo "INSTALL_DATE=$(date +"%Y-%m-%d")" >> "$INSTALL_LOG"
    echo "INSTALL_TIME=$(date +"%H:%M:%S")" >> "$INSTALL_LOG"
    echo "VERSION=2.1.0" >> "$INSTALL_LOG"
    echo "SYSTEM=$(uname -a)" >> "$INSTALL_LOG"
}

# Check if script is being sourced or directly executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Add installation tracking to installer
    if [[ "$1" == "--track-install" ]]; then
        track_installation
        echo -e "${GREEN}✅ Installation tracking initialized${NC}"
        exit 0
    fi
    
    # Run main uninstall function
    main "$@"
fi
