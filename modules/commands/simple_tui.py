"""
Simple TUI compatibility stub
Re-exports components from modular TUI system for backward compatibility
"""

# Re-export StatusLine components from modular system
try:
    from modules.tui.status_lines import StatusLine, PerformanceStatusLine, RefactoringStatusLine
    from modules.tui.core import OpenCLITUI
except (ImportError, ValueError):
    from tui.status_lines import StatusLine, PerformanceStatusLine, RefactoringStatusLine
    from tui.core import OpenCLITUI

# Legacy compatibility exports
__all__ = [
    'StatusLine',
    'PerformanceStatusLine', 
    'RefactoringStatusLine',
    'OpenCLITUI'
]

# Deprecated notice for new development
import warnings
warnings.warn(
    "simple_tui module is deprecated. Use modular tui.* components instead.",
    DeprecationWarning,
    stacklevel=2
)