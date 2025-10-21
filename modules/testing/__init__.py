"""
OpenCLI Testing Framework
=========================

Comprehensive testing tools for OpenCLI TUI with automated data collection,
visual testing, and function-level failure analysis.
"""

from .tui_test_framework import (
    TUITestFramework,
    TestStep,
    TestStepConfig,
    TestResult,
    create_permission_buffer_test
)

__all__ = [
    'TUITestFramework',
    'TestStep',
    'TestStepConfig',
    'TestResult',
    'create_permission_buffer_test'
]

__version__ = '1.0.0'
