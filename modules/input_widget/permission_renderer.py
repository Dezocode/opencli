"""
Permission prompt rendering for MultiLineInput
Handles visual display of permission prompts inline in the input box
"""

from rich.text import Text
from rich.style import Style

try:
    from modules.frontier_colors import FRONTIER_COLORS
except ImportError:
    try:
        from frontier_colors import FRONTIER_COLORS
    except ImportError:
        # Fallback if not available
        FRONTIER_COLORS = {}


def render_permission_prompt(prompt_data: dict, selected_option: int) -> Text:
    """
    Render permission prompt with Frontier colors

    Args:
        prompt_data: Dict with 'title', 'message', 'options', 'workflow_status'
        selected_option: Index of currently selected option

    Returns:
        Rich Text object with formatted prompt
    """
    output = Text()

    # Get data
    title = prompt_data.get('title', 'Permission')
    message = prompt_data.get('message', '')
    options = prompt_data.get('options', [])
    workflow_status = prompt_data.get('workflow_status')

    # Frontier colors
    title_color = FRONTIER_COLORS.get("warning", "#E2A478")
    text_color = FRONTIER_COLORS.get("text_primary", "#B3B1AD")
    selected_color = FRONTIER_COLORS.get("success", "#6B9E78")
    dim_color = FRONTIER_COLORS.get("text_dim", "#5C6773")
    error_color = FRONTIER_COLORS.get("error", "#D95757")
    info_color = FRONTIER_COLORS.get("info", "#6B9E78")

    # Title
    output.append(f"{title}\n", style=Style(color=title_color, bold=True))
    output.append("\n")

    # Workflow progress (if present)
    if workflow_status:
        steps = workflow_status.get('steps', [])
        current_step = workflow_status.get('current_step', 0)

        # Show progress bar
        total = len(steps)
        completed = sum(1 for s in steps if s.get('status') == 'completed')
        output.append(f"Progress: {completed}/{total} steps\n", style=Style(color=info_color))
        output.append("\n")

        # Show step list with status indicators
        for i, step in enumerate(steps):
            step_status = step.get('status', 'pending')
            step_title = step.get('title', f'Step {i+1}')

            # Status indicator
            if step_status == 'completed':
                indicator = "✓"
                style_color = selected_color
            elif step_status == 'failed':
                indicator = "✗"
                style_color = error_color
            elif step_status == 'in_progress':
                indicator = "⋯"
                style_color = info_color
            elif i == current_step:
                indicator = "▸"
                style_color = text_color
            else:
                indicator = "·"
                style_color = dim_color

            output.append(f"{indicator} ", style=Style(color=style_color))
            output.append(f"{step_title}\n", style=Style(color=style_color))

            # Show error if failed
            if step_status == 'failed' and step.get('error'):
                output.append(f"  Error: {step.get('error')}\n", style=Style(color=error_color))

        output.append("\n")

    # Message (with Rich markup support)
    try:
        # Text.from_markup() handles [color] tags properly
        markup_text = Text.from_markup(message)
        output.append(markup_text)
        # Add newline if message doesn't end with one
        if not message.endswith('\n'):
            output.append("\n")
    except Exception:
        # Fallback to plain text if markup parsing fails
        for line in message.split('\n'):
            if line.strip():
                output.append(line + "\n", style=Style(color=text_color))

    output.append("\n")

    # Options (only show if there are options)
    if options:
        for i, option in enumerate(options):
            option_text = option.get('text', '')
            if i == selected_option:
                # Selected - highlighted with arrow
                output.append("▸ ", style=Style(color=selected_color, bold=True))
                output.append(option_text + "\n", style=Style(color=selected_color, bold=True))
            else:
                # Not selected
                output.append("  ", style=Style(color=dim_color))
                output.append(option_text + "\n", style=Style(color=text_color))

    return output
