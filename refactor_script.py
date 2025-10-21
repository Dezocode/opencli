import re
import os

files_to_fix = [
    "modules/commands/basic_commands.py",
    "modules/commands/agent_commands.py",
    "modules/commands/diff_commands.py",
    "modules/commands/dev_commands.py",
    "modules/commands/model_commands.py",
    "modules/commands/provider_commands.py",
    "modules/commands/local_commands.py",
    "modules/commands/spec_commands.py",
    "modules/commands/refactor_commands.py",
    "modules/commands/system_commands.py",
    "modules/commands/inject_commands.py",
    "modules/docker_commands.py",
]

# Pattern to find the broken return statement and the preceding buffer_manager line.
return_pattern = re.compile(
    r"buffer_manager\s*=\s*get_permission_buffer_manager\(\)\s*\n\s*return await buffer_manager.request_permission\([^)]*\)",
    re.MULTILINE
)
replacement = "return prompt_data"

signature_pattern = re.compile(r"(async def\s+)(\w+_prompt)")
sig_replacement = r"def \2"

total_fixed = 0
for file_path in files_to_fix:
    if not os.path.exists(file_path):
        print(f"Skipping non-existent file: {file_path}")
        continue

    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        continue

    # First, replace the broken return statements
    content, returns_fixed = return_pattern.subn(replacement, content)
    
    # Second, fix the async def signatures
    content, sigs_fixed = signature_pattern.subn(sig_replacement, content)

    if returns_fixed > 0 or sigs_fixed > 0:
        print(f"Corrected {file_path}: Fixed {returns_fixed} return statements and {sigs_fixed} function signatures.")
        total_fixed += returns_fixed
        try:
            with open(file_path, 'w') as f:
                f.write(content)
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
    else:
        print(f"No issues found in {file_path}.")

print(f"\n✅ Refactoring complete. Fixed a total of {total_fixed} prompt functions.")