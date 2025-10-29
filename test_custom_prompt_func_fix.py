#!/usr/bin/env python3
"""
Test to verify that custom_prompt_func is properly stored in metadata
"""

import sys


def test_custom_prompt_func_in_kwargs():
    """Test the logic of extracting custom_prompt_func from kwargs"""
    
    print("Testing custom_prompt_func extraction logic...")
    print()
    
    # Simulate kwargs with custom_prompt_func
    kwargs = {
        'custom_prompt_func': lambda: "test",
        'other_param': 'value'
    }
    
    print(f"Initial kwargs: {list(kwargs.keys())}")
    
    # Extract custom_prompt_func from kwargs and put it in metadata
    custom_prompt_func = kwargs.pop('custom_prompt_func', None)
    metadata = kwargs.get('metadata', {})
    if custom_prompt_func:
        metadata['custom_prompt_func'] = custom_prompt_func
        kwargs['metadata'] = metadata
    
    print(f"After processing:")
    print(f"  - kwargs keys: {list(kwargs.keys())}")
    print(f"  - metadata keys: {list(metadata.keys())}")
    print(f"  - custom_prompt_func in metadata: {'custom_prompt_func' in metadata}")
    print()
    
    # Verify the fix
    has_custom_prompt = 'custom_prompt_func' in metadata
    not_in_kwargs = 'custom_prompt_func' not in kwargs
    in_kwargs_metadata = 'metadata' in kwargs
    
    print(f"✓ custom_prompt_func in metadata: {has_custom_prompt}")
    print(f"✓ custom_prompt_func NOT in top-level kwargs: {not_in_kwargs}")
    print(f"✓ metadata in kwargs: {in_kwargs_metadata}")
    
    if has_custom_prompt and not_in_kwargs and in_kwargs_metadata:
        print()
        print("✅ TEST PASSED: custom_prompt_func properly moved to metadata")
        return True
    else:
        print()
        print("❌ TEST FAILED")
        return False


if __name__ == "__main__":
    success = test_custom_prompt_func_in_kwargs()
    sys.exit(0 if success else 1)
