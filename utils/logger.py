"""
Enterprise Logging Configuration
Structured logging with security and audit capabilities
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if hasattr(record, 'user'):
            log_entry['user'] = record.user
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def setup_logger(name: str = "cyberzilla", log_level: str = "INFO") -> logging.Logger:
    """Setup enterprise logger"""
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler (rich formatting)
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # File handler (JSON format)
    file_handler = RotatingFileHandler(
        "logs/cyberzilla.json.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    
    # Error file handler
    error_handler = RotatingFileHandler(
        "logs/cyberzilla.errors.log", 
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger

# Security-specific logger
def get_security_logger():
    """Get security-specific logger"""
    logger = setup_logger("security")
    
    # Add audit log handler
    audit_handler = RotatingFileHandler(
        "logs/security_audit.log",
        maxBytes=5*1024*1024,
        backupCount=10
    )
    audit_format = logging.Formatter(
        '%(asctime)s | SECURITY | %(levelname)s | %(message)s'
    )
    audit_handler.setFormatter(audit_format)
    audit_handler.setLevel(logging.INFO)
    
    logger.addHandler(audit_handler)
    return logger
