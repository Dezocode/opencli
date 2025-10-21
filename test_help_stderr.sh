#!/bin/bash
# Test /help and capture stderr debug output

python3 ~/.opencli/opencli.py tui 2>&1 &
pid=$!

sleep 4

# Send /help via automation
python3 -c "
import pexpect
import time

child = pexpect.spawn('python3 ~/.opencli/opencli.py tui', encoding='utf-8', timeout=5)
time.sleep(3)
child.sendline('/help')
time.sleep(2)
child.send('\x03')  # Ctrl+C
try:
    child.expect(pexpect.EOF, timeout=2)
except:
    pass
print(child.before)
" 2>&1 | grep -E "PermissionBuffer|permission|request_permission|custom_prompt" | head -50

kill $pid 2>/dev/null || true
