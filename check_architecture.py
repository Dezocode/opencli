#!/usr/bin/env python3
"""
Standalone script to check architecture compliance
Run: python check_architecture.py
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from architecture_checker import check_architecture, ArchitectureChecker

def main():
    print("🔍 Checking OpenCLI architecture compliance...\n")

    # Run the check
    report = check_architecture("architecture.yml")

    # Format and display report
    checker = ArchitectureChecker("architecture.yml")
    formatted_report = checker.format_report(report)

    print(formatted_report)

    # Exit with error code if violations found
    sys.exit(1 if report.has_errors() else 0)

if __name__ == "__main__":
    main()
