#!/usr/bin/env python3
"""
Replace emojis with Frontier color styling in async_interactive.py
"""

import re

# Emoji to Frontier color mapping
REPLACEMENTS = [
    # Debug messages
    (r'🐛 STALL DEBUG:', 'DEBUG:'),
    (r'🐛 STREAM:', 'STREAM:'),
    (r'🐛 POST-STREAM:', 'POST-STREAM:'),
    (r'🐛 TOOL EXEC:', 'TOOL:'),
    (r'🐛 CONTINUATION STREAM:', 'CONTINUATION:'),
    (r'🐛 RECURSIVE TOOLS:', 'RECURSIVE:'),
    (r'🐛 Starting tool execution:', 'TOOL:'),
    (r'🐛 Debug mode', 'Debug mode'),
    (r'🐛', 'DEBUG'),

    # Info/Search messages
    (r'🔍 DEBUG:', 'DEBUG:'),
    (r'🔍 Checking model availability', 'Checking model availability'),
    (r'🔍 Auto-configuring headers', 'Auto-configuring headers'),
    (r'🔍 BLOCKING THREAD DETECTION', 'BLOCKING THREAD DETECTION'),
    (r'🔍', '→'),

    # Success markers
    (r'✅', '✓'),
    (r'✓ Goal Check:', '✓'),

    # Error markers
    (r'❌ Operation cancelled', '✗ Operation cancelled'),
    (r'❌ API request timed out', '✗ API request timed out'),
    (r'❌ API Error', '✗ API Error'),
    (r'❌ Streaming Error:', '✗ Streaming Error:'),
    (r'❌', '✗'),

    # Warning markers
    (r'⚠️  PAID MODEL WARNING', '! PAID MODEL WARNING'),
    (r'⚠️  Warning: Low Model Availability', '! Warning: Low Model Availability'),
    (r'⚠️  FOUND (.*) POTENTIALLY BLOCKED THREADS', r'! FOUND \1 POTENTIALLY BLOCKED THREADS'),
    (r'⚠️  PERFORMANCE BUDGET VIOLATIONS', '! PERFORMANCE BUDGET VIOLATIONS'),
    (r'⚠️  Auto-refactoring', '! Auto-refactoring'),
    (r'⚠️  Result too large', '! Result too large'),
    (r'⚠️  No header changes', '! No header changes'),
    (r'⚠️ The API did not respond', '! The API did not respond'),
    (r'⚠️ You can continue chatting', '! You can continue chatting'),
    (r'⚠️ Chunk #', '! Chunk #'),
    (r'⚠️ API rejected', '! API rejected'),
    (r'⚠️ Permission check error', '! Permission check error'),
    (r'⚠️ Note: Markdown formatting', '! Note: Markdown formatting'),
    (r'⚠️⚠️⚠️', '!!!'),
    (r'⚠️', '!'),

    # Tool/Settings markers
    (r'🔧 Quick Commands:', '▸ Quick Commands:'),
    (r'🔧 Refactoring Commands', '▸ Refactoring Commands'),
    (r'⚙ ', '▸ '),
    (r'⚙', '▸'),

    # Stats markers
    (r'📊 Shell Injection Logs', '▪ Shell Injection Logs'),
    (r'📊 Refactoring Analysis:', '▪ Refactoring Analysis:'),
    (r'📊 PERFORMANCE PROFILE', '▪ PERFORMANCE PROFILE'),
    (r'📊 Performance monitoring enabled', '▪ Performance monitoring enabled'),
    (r'📊 Performance monitoring disabled', '▪ Performance monitoring disabled'),
    (r'📊 Result size:', 'Result size:'),
    (r'📊 ', '▪ '),
    (r'📊', '▪'),

    # Speed/Fast mode markers
    (r'⚡ Fast mode', '» Fast mode'),
    (r'⚡ Token streaming speed', '» Token streaming speed'),
    (r'⚡', '»'),

    # Tips
    (r'💡 ', '→ '),
    (r'💡', '→'),

    # Pause
    (r'⏸  Refactoring system stopped', '‖ Refactoring system stopped'),
    (r'⏸', '‖'),

    # Misc icons
    (r'🟢 CPU usage', 'CPU usage'),
    (r'💾 Memory', 'Memory'),
    (r'🧵 Thread', 'Thread'),
    (r'🔴 Current bottlenecks', 'Bottlenecks'),
]

def remove_emojis(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated {filepath}")
        return True
    else:
        print(f"No changes needed for {filepath}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "/Users/dezmondhollins/.opencli/modules/async_interactive.py"

    remove_emojis(filepath)
