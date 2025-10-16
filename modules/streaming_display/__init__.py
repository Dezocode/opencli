"""
Streaming Display System - Modular architecture
Extracted from monolithic streaming_display.py for better maintainability
"""

from .core import StreamingDisplay
from .selection import TextSelection
from .markdown import MarkdownProcessor
from .buffers import BufferManager
from .mouse import MouseHandler

__all__ = [
    'StreamingDisplay',
    'TextSelection', 
    'MarkdownProcessor',
    'BufferManager',
    'MouseHandler'
]

# Version and metadata
__version__ = '2.0.0'
__description__ = 'Modular streaming display system for OpenCLI'