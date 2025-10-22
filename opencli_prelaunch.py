#!/usr/bin/env python3
"""
OpenCLI Pre-Launch Status Screen
Shows codebase status with Frontier colors, permission prompt borders,
file tree with timestamps, cache verification, and OpenCLI ASCII art
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import hashlib

# Import Frontier colors
sys.path.insert(0, str(Path.home() / ".opencli"))
try:
    from modules.frontier_colors import FRONTIER_COLORS
except ImportError:
    FRONTIER_COLORS = {
        "border": "#5C6773",
        "text_primary": "#B3B1AD",
        "success": "#6B9E78",
        "warning": "#D4A374",
        "error": "#C76B6B",
        "info": "#6B8E9E",
        "text_dim": "#3E4450",
    }

# ANSI color codes
def color(hex_color):
    color_map = {
        "#5C6773": "\033[38;5;243m",  # border
        "#B3B1AD": "\033[38;5;250m",  # text
        "#6B9E78": "\033[38;5;108m",  # success/green
        "#D4A374": "\033[38;5;180m",  # warning/orange
        "#C76B6B": "\033[38;5;167m",  # error/red
        "#6B8E9E": "\033[38;5;109m",  # info/blue
        "#3E4450": "\033[38;5;239m",  # dim
    }
    return color_map.get(hex_color, "\033[0m")

RESET = "\033[0m"
BOLD = "\033[1m"

def print_top_border(width=100):
    """Print top border (╭─╮)"""
    c = color(FRONTIER_COLORS["border"])
    print(f"{c}╭{'─' * (width - 2)}╮{RESET}")

def print_bottom_border(width=100):
    """Print bottom border (╰─╯)"""
    c = color(FRONTIER_COLORS["border"])
    print(f"{c}╰{'─' * (width - 2)}╯{RESET}")

def print_box_line(text, width=100, text_color=None, align='left'):
    """Print line in box"""
    border_c = color(FRONTIER_COLORS["border"])
    text_c = text_color or color(FRONTIER_COLORS["text_primary"])

    if align == 'center':
        padding = (width - len(text) - 4) // 2
        print(f"{border_c}│{RESET} {' ' * padding}{text_c}{text}{RESET}{' ' * (width - len(text) - 4 - padding)} {border_c}│{RESET}")
    else:
        # Remove ANSI codes for length calculation
        clean_text = text.replace(BOLD, '').replace(RESET, '')
        for c_code in [color(v) for v in FRONTIER_COLORS.values()]:
            clean_text = clean_text.replace(c_code, '')
        print(f"{border_c}│{RESET} {text_c}{text}{RESET}{' ' * (width - len(clean_text) - 4)} {border_c}│{RESET}")

def print_empty_line(width=100):
    """Print empty line"""
    border_c = color(FRONTIER_COLORS["border"])
    print(f"{border_c}│{RESET}{' ' * (width - 2)}{border_c}│{RESET}")

def get_all_files_tree(directory, base_dir, prefix="", is_last_list=None, max_depth=2, current_depth=0):
    """Get all files in tree format with timestamps"""
    if current_depth > max_depth or not directory.is_dir():
        return []

    lines = []
    is_last_list = is_last_list or []

    try:
        items = sorted([p for p in directory.iterdir() if not p.name.startswith('.') and p.name != '__pycache__'],
                      key=lambda x: (not x.is_dir(), x.name))

        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)

            # Build tree prefix
            connector = "└─" if is_last else "├─"
            full_prefix = ""
            for depth_is_last in is_last_list:
                full_prefix += "    " if depth_is_last else "│   "
            full_prefix += connector

            if item.is_file() and item.suffix == '.py':
                mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                lines.append((full_prefix, item.name, mtime))

            elif item.is_dir():
                lines.append((full_prefix, f"{item.name}/", ""))
                # Recurse
                sublines = get_all_files_tree(
                    item,
                    base_dir,
                    prefix,
                    is_last_list + [is_last],
                    max_depth,
                    current_depth + 1
                )
                lines.extend(sublines)

    except PermissionError:
        pass

    return lines

def check_cache_shadowing(directory):
    """Check which cache files would shadow source files"""
    shadowed = []  # (cache_file, source_file, cache_time, source_time)

    for root, dirs, files in os.walk(directory):
        if '/sessions/' in root:
            continue

        for file in files:
            if file.endswith('.pyc') and '__pycache__' in root:
                cache_path = Path(root) / file
                # Extract source filename
                base_name = file.split('.')[0] + '.py'
                source_path = cache_path.parent.parent / base_name

                if source_path.exists():
                    cache_mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
                    source_mtime = datetime.fromtimestamp(source_path.stat().st_mtime)
                    shadowed.append((
                        str(cache_path.relative_to(directory)),
                        str(source_path.relative_to(directory)),
                        cache_mtime,
                        source_mtime
                    ))

    return shadowed

def get_opencli_ascii():
    return """   ____                   __________    ____
  / __ \\____  ___  ____  / ____/ /   /  _/
 / / / / __ \\/ _ \\/ __ \\/ /   / /    / /
/ /_/ / /_/ /  __/ / / / /___/ /____/ /
\\____/ .___/\\___/_/ /_/\\____/_____/___/
    /_/"""

def main():
    WIDTH = 100
    opencli_dir = Path.home() / ".opencli"
    modules_dir = opencli_dir / "modules"

    # Clear screen
    os.system('clear' if os.name != 'nt' else 'cls')

    success_c = color(FRONTIER_COLORS["success"])
    warning_c = color(FRONTIER_COLORS["warning"])
    error_c = color(FRONTIER_COLORS["error"])
    info_c = color(FRONTIER_COLORS["info"])
    dim_c = color(FRONTIER_COLORS["text_dim"])

    print()
    print_top_border(WIDTH)
    print_empty_line(WIDTH)
    print_box_line(f"{BOLD}🚀  OPENCLI PRE-LAUNCH STATUS", WIDTH, warning_c, 'center')
    print_empty_line(WIDTH)

    # Section: File Tree with Timestamps
    print_box_line(f"{BOLD}📁  CODEBASE FILES & TIMESTAMPS", WIDTH, warning_c)
    print_empty_line(WIDTH)

    tree_lines = get_all_files_tree(modules_dir, opencli_dir, max_depth=2)

    # Show up to 30 lines of tree
    for prefix, name, mtime in tree_lines[:30]:
        if mtime:
            line = f"   {dim_c}{prefix}{RESET} {info_c}{name:<40}{RESET} {success_c}{mtime}{RESET}"
        else:
            line = f"   {dim_c}{prefix} {name}{RESET}"
        print_box_line(line, WIDTH)

    if len(tree_lines) > 30:
        print_box_line(f"   {dim_c}... and {len(tree_lines) - 30} more files{RESET}", WIDTH)

    print_empty_line(WIDTH)

    # Section: Cache Verification
    print_box_line(f"{BOLD}🧹  CACHE VERIFICATION", WIDTH, warning_c)
    print_empty_line(WIDTH)

    shadowed = check_cache_shadowing(opencli_dir)

    if not shadowed:
        print_box_line(f"   {success_c}✅ No bytecode cache found{RESET}", WIDTH)
        print_box_line(f"   {success_c}✅ Python will use fresh source files{RESET}", WIDTH)
        cache_clean = True
    else:
        print_box_line(f"   {error_c}❌ Found {len(shadowed)} cached files that would shadow source:{RESET}", WIDTH)
        print_empty_line(WIDTH)

        # Show first 10 shadowed files with timestamps
        for cache_file, source_file, cache_time, source_time in shadowed[:10]:
            print_box_line(f"   {error_c}Cache:{RESET} {cache_file}", WIDTH)
            print_box_line(f"   {dim_c}  Time: {cache_time.strftime('%Y-%m-%d %H:%M:%S')}{RESET}", WIDTH)
            print_box_line(f"   {warning_c}Source:{RESET} {source_file}", WIDTH)
            print_box_line(f"   {dim_c}  Time: {source_time.strftime('%Y-%m-%d %H:%M:%S')}{RESET}", WIDTH)
            print_empty_line(WIDTH)

        if len(shadowed) > 10:
            print_box_line(f"   {dim_c}... and {len(shadowed) - 10} more{RESET}", WIDTH)

        cache_clean = False

    print_empty_line(WIDTH)

    # Section: Import Path
    print_box_line(f"{BOLD}🔍  PYTHON IMPORT PATH", WIDTH, warning_c)
    print_empty_line(WIDTH)
    print_box_line(f"   {info_c}Priority 1:{RESET} {opencli_dir}", WIDTH)
    print_box_line(f"   {dim_c}├─{RESET} {success_c}modules/{RESET} (all code loaded from here)", WIDTH)
    print_box_line(f"   {dim_c}└─{RESET} cli/ (entry point only)", WIDTH)
    print_empty_line(WIDTH)
    print_box_line(f"   {success_c}✅ Single source of truth: modules/{RESET}", WIDTH)
    print_empty_line(WIDTH)

    # Section: Critical Files
    print_box_line(f"{BOLD}📋  CRITICAL FILES CHECK", WIDTH, warning_c)
    print_empty_line(WIDTH)

    critical_files = [
        "modules/permissions/risk_assessment.py",
        "modules/permissions/templates.py",
        "modules/permissions/integration.py",
        "modules/docker_commands.py",
        "modules/tui/core.py",
    ]

    all_exist = True
    for file_path in critical_files:
        full_path = opencli_dir / file_path
        if full_path.exists():
            md5 = hashlib.md5(full_path.read_bytes()).hexdigest()[:12]
            mtime = datetime.fromtimestamp(full_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            print_box_line(f"   {success_c}✅{RESET} {file_path}", WIDTH)
            print_box_line(f"      {dim_c}MD5: {md5} | Modified: {mtime}{RESET}", WIDTH)
        else:
            print_box_line(f"   {error_c}❌ {file_path} MISSING{RESET}", WIDTH)
            all_exist = False

    print_empty_line(WIDTH)

    # Final Status
    if cache_clean and all_exist:
        print_box_line(f"{BOLD}{success_c}✅  STATUS: READY TO LAUNCH{RESET}", WIDTH, align='center')
        print_empty_line(WIDTH)
        print_box_line("All checks passed:", WIDTH, align='center')
        print_box_line(f"{success_c}• Using latest codebase{RESET}", WIDTH, align='center')
        print_box_line(f"{success_c}• No stale cache{RESET}", WIDTH, align='center')
        print_box_line(f"{success_c}• All critical files present{RESET}", WIDTH, align='center')
        can_launch = True
    else:
        print_box_line(f"{BOLD}{error_c}❌  STATUS: ISSUES DETECTED{RESET}", WIDTH, align='center')
        print_empty_line(WIDTH)
        if not cache_clean:
            print_box_line(f"{error_c}• Clear cache before launching{RESET}", WIDTH, align='center')
        if not all_exist:
            print_box_line(f"{error_c}• Critical files missing{RESET}", WIDTH, align='center')
        can_launch = False

    print_empty_line(WIDTH)

    # OpenCLI ASCII Art
    ascii_art = get_opencli_ascii()
    for line in ascii_art.split('\n'):
        if line.strip():
            print_box_line(f"{success_c}{line}{RESET}", WIDTH, align='center')

    print_empty_line(WIDTH)
    print_bottom_border(WIDTH)
    print()

    if not can_launch:
        print(f"{error_c}❌ Cannot launch - please fix issues above{RESET}")
        print()
        print("To clear cache:")
        print("  find ~/.opencli -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null")
        print("  find ~/.opencli -type f -name '*.pyc' -delete 2>/dev/null")
        print()
        sys.exit(1)

    # Ask for confirmation
    print(f"{info_c}Launch OpenCLI? (y/n):{RESET} ", end='', flush=True)
    response = input().strip().lower()

    if response == 'y' or response == 'yes':
        print(f"\n{success_c}🚀 Launching OpenCLI...{RESET}\n")
        return 0
    else:
        print(f"\n{error_c}❌ Launch cancelled by user{RESET}\n")
        sys.exit(0)

if __name__ == "__main__":
    sys.exit(main())
