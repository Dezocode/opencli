#!/usr/bin/env python3
"""
Test the opencli command directly like a user would
"""

import subprocess
import sys
import time
from pathlib import Path

def test_opencli_directly():
    """Test opencli like a user would use it"""
    
    # Test 1: Try fallback mode
    print("Testing opencli --fallback mode...")
    
    try:
        # Start opencli in fallback mode
        cmd = [sys.executable, "/Users/dezmondhollins/.opencli/opencli.py", "--fallback"]
        
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/Users/dezmondhollins/.opencli"
        )
        
        # Send a test message
        test_message = "hello world\n"
        
        print(f"Sending message: '{test_message.strip()}'")
        
        # Write the message and close stdin
        proc.stdin.write(test_message)
        proc.stdin.close()
        
        # Wait a bit for output
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            print("Process timed out")
        
        print("STDOUT:")
        print(stdout)
        print("\nSTDERR:")
        print(stderr)
        print(f"\nReturn code: {proc.returncode}")
        
    except Exception as e:
        print(f"Error testing opencli: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_opencli_directly()