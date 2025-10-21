#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "🚀 Starting OpenCLI installation/update..."

# Define source and destination directories
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
DEST_DIR="$HOME/.opencli"
BIN_DIR="$HOME/bin"

echo "Source: $SOURCE_DIR"
echo "Destination: $DEST_DIR"

# Create destination directories
mkdir -p "$DEST_DIR/modules"
mkdir -p "$DEST_DIR/agents"
mkdir -p "$BIN_DIR"

# Sync modules and agents directories using rsync for efficiency
echo "  syncing modules..."
rsync -av --delete "$SOURCE_DIR/modules/" "$DEST_DIR/modules/"

echo " syncing agents..."
rsync -av --delete "$SOURCE_DIR/agents/" "$DEST_DIR/agents/"

# Copy top-level files
echo " installing top-level files..."
cp "$SOURCE_DIR/opencli.py" "$DEST_DIR/"
cp "$SOURCE_DIR/version.json" "$DEST_DIR/"
cp "$SOURCE_DIR/requirements.txt" "$DEST_DIR/"

# Create the executable in ~/bin
EXECUTABLE_PATH="$BIN_DIR/opencli"
echo " creating executable at $EXECUTABLE_PATH..."

# Create a more robust Python-based wrapper script
cat > "$EXECUTABLE_PATH" << EOL
#!/usr/bin/env python3
import sys
import os
import subprocess

dest_dir = os.path.expanduser("~/.opencli")
script_path = os.path.join(dest_dir, "opencli.py")

# Ensure the python executable used to run this wrapper is used for the main script
python_executable = sys.executable
if not python_executable:
    print("Error: Could not determine Python executable.", file=sys.stderr)
    sys.exit(1)

try:
    # Use execvp to replace the wrapper process with the main script
    os.execvp(python_executable, [python_executable, script_path] + sys.argv[1:])
except FileNotFoundError:
    print(f"Error: Could not find the main script at {script_path}", file=sys.stderr)
    sys.exit(1)
EOL

# Make the wrapper script executable
chmod +x "$EXECUTABLE_PATH"

echo "✅ OpenCLI installation/update complete."
echo "Ensure '$BIN_DIR' is in your shell's PATH."
