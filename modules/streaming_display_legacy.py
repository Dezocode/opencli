"""
Streaming Display - Legacy Compatibility Layer
Re-exports from modular streaming_display system for backward compatibility
"""

# Re-export the main StreamingDisplay class from the modular system
from .streaming_display import StreamingDisplay

# Legacy compatibility exports
__all__ = [
    'StreamingDisplay'
]

# Deprecation warning for new development
import warnings
warnings.warn(
    "Direct streaming_display module import is deprecated. Use modular streaming_display.* components instead.",
    DeprecationWarning,
    stacklevel=2
)