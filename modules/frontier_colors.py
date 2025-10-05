"""
Frontier CLI Color Scheme
Professional, subtle colors inspired by modern terminal UIs
"""

# Terminal-inspired palette - subtle and professional
FRONTIER_COLORS = {
    # Base colors - very subtle
    "background": "#0A0E14",      # Very dark blue-black
    "surface": "#151A21",          # Slightly lighter for input
    "border": "#1F2430",           # Subtle border
    "border_focused": "#3E4B59",   # Slightly brighter when focused

    # Text colors - muted and readable
    "text_primary": "#B3B1AD",     # Soft white-gray (main text)
    "text_secondary": "#5C6773",   # Muted gray (secondary text)
    "text_dim": "#3E4450",         # Very muted (timestamps, hints)

    # Semantic colors - desaturated
    "success": "#6B9E78",          # Muted green
    "warning": "#D4A374",          # Muted orange
    "error": "#C76B6B",            # Muted red
    "info": "#6B8E9E",             # Muted blue
    "accent": "#7B91A3",           # Muted blue-gray (links, highlights)

    # Code highlighting - subtle
    "code_bg": "#0F1419",          # Slightly darker than background
    "code_text": "#89B8C2",        # Soft cyan for code
    "code_keyword": "#A3BE8C",     # Soft green for keywords
    "code_string": "#C9A28D",      # Soft tan for strings
    "code_comment": "#4D5563",     # Very muted for comments

    # User/AI indicators
    "user_name": "#7B91A3",        # Soft blue
    "ai_name": "#89B8C2",          # Soft cyan
    "prompt_symbol": "#6B9E78",    # Muted green for prompt

    # Markdown elements
    "heading": "#A3BE8C",          # Soft green for headings
    "bold": "#B3B1AD",             # Same as primary but will use bold weight
    "italic": "#8FA1B3",           # Slightly blue-tinted
    "link": "#6B8E9E",             # Muted blue
    "inline_code": "#D4A374",      # Muted orange
    "list_marker": "#7B91A3",      # Soft blue-gray
}

# Laser effect colors - smooth frontier gradient
FRONTIER_LASER_COLORS = [
    "#3E4450",  # Deep slate (very subtle start)
    "#4D5563",  # Muted gray-blue
    "#5C6773",  # Subtle gray
    "#6B8E9E",  # Muted blue (accent)
    "#7B91A3",  # Soft blue-gray
    "#89B8C2",  # Soft cyan (AI name color)
    "#A3BE8C",  # Soft green (success color)
    "#B3B1AD",  # Primary text (bright end)
]

# Status line colors
STATUS_COLORS = {
    "model": "#89B8C2",      # Soft cyan
    "tokens": "#A3BE8C",     # Soft green
    "turn": "#7B91A3",       # Soft blue-gray
    "cwd": "#D4A374",        # Muted orange
    "time": "#5C6773",       # Muted gray
}
