#!/usr/bin/env python3
"""
Diagnostic script to test TUI startup and identify immediate exit issues
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def main():
    """Test TUI startup with detailed logging"""

    print("\n" + "="*80)
    print("TUI STARTUP DIAGNOSTIC")
    print("="*80 + "\n")

    # Create minimal config
    config = {
        "model": "gpt-4",
        "apiKey": "test-key",
        "contextWindow": 128000
    }

    # Create session
    from cli.session import Session
    session = Session(model="gpt-4")

    print("✓ Session created")

    # Import and run interactive_async with exception handling
    try:
        from modules.async_interactive import interactive_async
        print("✓ interactive_async imported")

        print("\n" + "-"*80)
        print("STARTING TUI - Watch for immediate exit issues")
        print("-"*80 + "\n")

        await interactive_async(config, session)

        print("\n" + "-"*80)
        print("TUI EXITED NORMALLY")
        print("-"*80 + "\n")

    except KeyboardInterrupt:
        print("\n\n✓ User interrupted (Ctrl+C)")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
