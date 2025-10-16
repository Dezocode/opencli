"""
Permission system enums and constants
Priority levels, states, and configuration
"""

from enum import Enum


class PromptPriority(Enum):
    """Priority levels for permission prompts (Constitution compliant)"""
    LOW = 3
    NORMAL = 2  
    HIGH = 1
    URGENT = 0  # Highest priority


class PromptState(Enum):
    """States for permission prompts"""
    QUEUED = "queued"
    DISPLAYING = "displaying" 
    AWAITING_INPUT = "awaiting_input"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"
    AUTO_DISMISSED = "auto_dismissed"


class SDKState(Enum):
    """SDK initialization states"""
    UNINITIALIZED = "uninitialized"
    STARTING = "starting"
    BACKGROUND_INIT = "background_init"
    REGISTERING = "registering"
    ENFORCING = "enforcing"  
    INITIALIZED = "initialized"
    FAILED = "failed"
    DEGRADED_MODE = "degraded_mode"


class PermissionResponse(Enum):
    """Permission response types"""
    ALLOW_ONCE = "allow_once"
    ALLOW_SESSION = "allow_session"
    ALLOW_ALWAYS = "allow_always"
    ALLOW_DOMAIN = "allow_domain"
    DENY = "deny"
    CANCEL = "cancel"


# Constitution v3.0.0 compliance constants
CONSTITUTION_UI_RESPONSE_LIMIT_MS = 50
CONSTITUTION_CANCELLATION_LIMIT_MS = 100
CONSTITUTION_NAVIGATION_AUTO_DISMISS = True

# Default configuration values
DEFAULT_CACHE_TTL_SECONDS = 300  # 5 minutes
DEFAULT_MAX_CONCURRENT_PROMPTS = 3
DEFAULT_MAX_AUDIT_ENTRIES = 100
DEFAULT_MAX_CACHE_ENTRIES = 50
DEFAULT_MAX_RESPONSE_TIMES = 100

# Timeout and escalation settings
DEFAULT_AUTO_ESCALATION_TIMEOUT = 30.0  # seconds
DEFAULT_AUTO_DISMISS_TIMEOUT = 60.0     # seconds
DEFAULT_ORPHAN_CLEANUP_INTERVAL = 30.0  # seconds

# Internationalization settings
SUPPORTED_LOCALES = ['en', 'es', 'fr', 'de']
DEFAULT_LOCALE = 'en'

# Analytics and monitoring
ANALYTICS_ENABLED_BY_DEFAULT = True
PERFORMANCE_TRACKING_ENABLED = True
DETAILED_LOGGING_ENABLED = False