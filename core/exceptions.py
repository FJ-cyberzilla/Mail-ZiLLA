"""
Enterprise Exception Hierarchy
Custom exceptions for robust error handling
"""

class CyberzillaException(Exception):
    """Base exception for all Cyberzilla errors"""
    pass

class SecurityViolation(CyberzillaException):
    """Raised when security rules are violated"""
    pass

class AuthenticationError(CyberzillaException):
    """Authentication and authorization errors"""
    pass

class ConfigurationError(CyberzillaException):
    """Configuration-related errors"""
    pass

class ValidationError(CyberzillaException):
    """Data validation errors"""
    pass

class AgentError(CyberzillaException):
    """AI Agent execution errors"""
    pass

class ProxyError(CyberzillaException):
    """Proxy-related errors"""
    pass

class RateLimitExceeded(CyberzillaException):
    """Rate limiting violations"""
    pass

class DatabaseError(CyberzillaException):
    """Database operation errors"""
    pass

class NetworkError(CyberzillaException):
    """Network communication errors"""
    pass
