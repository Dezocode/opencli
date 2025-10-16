"""Permission buffer enums and constants"""

from enum import Enum


class PromptPriority(Enum):
    """Priority levels for permission prompts (Constitution compliant)"""
    LOW = 3
    NORMAL = 2  
    HIGH = 1
    URGENT = 0  # Highest priority


class PromptState(Enum):
    QUEUED = "queued"
    DISPLAYING = "displaying" 
    AWAITING_INPUT = "awaiting_input"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"
    AUTO_DISMISSED = "auto_dismissed"