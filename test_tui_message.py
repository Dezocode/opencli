#!/usr/bin/env python3
"""
Test TUI message sending by simulating Enter press
"""
import sys
import asyncio

# Add path
sys.path.insert(0, '.')

from modules.multiline_input import MultiLineInput

# Check the action_submit implementation
import inspect

print("=" * 70)
print("CHECKING MultiLineInput.action_submit() IMPLEMENTATION")
print("=" * 70)

source = inspect.getsource(MultiLineInput.action_submit)
print(source)

print("\n" + "=" * 70)
print("CHECKING MESSAGE CLASSES")
print("=" * 70)

# Check message classes
print(f"Submitted class: {MultiLineInput.Submitted}")
print(f"CommandSuggestionSelect class: {MultiLineInput.CommandSuggestionSelect}")

# Check if suggestions_active is an attribute
widget = MultiLineInput(placeholder="Test")
print(f"\nWidget has suggestions_active: {hasattr(widget, 'suggestions_active')}")
print(f"Initial value: {widget.suggestions_active}")

print("\n" + "=" * 70)
print("SIMULATING MESSAGE SUBMISSION")
print("=" * 70)

# Simulate typing a message
widget.value = "hello world"
widget.suggestions_active = False

print(f"Widget value: '{widget.value}'")
print(f"suggestions_active: {widget.suggestions_active}")

# Check what would happen if action_submit is called
if widget.suggestions_active:
    print("✗ Would post CommandSuggestionSelect (WRONG for regular message)")
else:
    if widget.value.strip():
        print("✓ Would post Submitted(value) message (CORRECT)")
    else:
        print("✗ Would NOT post message (value empty)")

print("\n" + "=" * 70)
print("CHECKING CommandHandlers")
print("=" * 70)

from modules.tui.command_handlers import CommandHandlers

# Check if handler exists
if hasattr(CommandHandlers, 'on_multi_line_input_submitted'):
    print("✓ on_multi_line_input_submitted handler exists")

    # Check signature
    sig = inspect.signature(CommandHandlers.on_multi_line_input_submitted)
    print(f"  Signature: {sig}")
else:
    print("✗ on_multi_line_input_submitted handler MISSING")

print("\n" + "=" * 70)
print("CHECKING OpenCLITUI INHERITANCE")
print("=" * 70)

from modules.tui.core import OpenCLITUI

# Check MRO (Method Resolution Order)
print("Method Resolution Order:")
for i, cls in enumerate(OpenCLITUI.__mro__):
    print(f"  {i}. {cls.__name__}")

# Check if OpenCLITUI has the handler
if hasattr(OpenCLITUI, 'on_multi_line_input_submitted'):
    print("\n✓ OpenCLITUI has on_multi_line_input_submitted (via inheritance)")
else:
    print("\n✗ OpenCLITUI MISSING on_multi_line_input_submitted")

# Check if _handle_user_message exists
if hasattr(OpenCLITUI, '_handle_user_message'):
    print("✓ OpenCLITUI has _handle_user_message")
    sig = inspect.signature(OpenCLITUI._handle_user_message)
    print(f"  Signature: {sig}")
else:
    print("✗ OpenCLITUI MISSING _handle_user_message")

print("\n" + "=" * 70)
print("RESULT")
print("=" * 70)

all_good = (
    hasattr(MultiLineInput, 'action_submit') and
    hasattr(widget, 'suggestions_active') and
    hasattr(CommandHandlers, 'on_multi_line_input_submitted') and
    hasattr(OpenCLITUI, 'on_multi_line_input_submitted') and
    hasattr(OpenCLITUI, '_handle_user_message')
)

if all_good:
    print("✓ All components are connected properly")
    print("\nIf messages still don't send, the issue is likely:")
    print("  1. Event not being posted from action_submit()")
    print("  2. Handler not being called (Textual message routing issue)")
    print("  3. Exception in _handle_user_message silently failing")
else:
    print("✗ COMPONENTS ARE MISSING - this explains the issue")
