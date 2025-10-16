"""
ANSI Background Support for Textual - REFACTORED
Configurable dual-mode color system using ColorManager
"""

from textual.app import App
from textual.color import Color as TextualColor
from textual.css.styles import RenderStyles
from rich.style import Style
from rich.console import Console
from rich.color import Color as RichColor

try:
    from .color_manager import ColorManager, ColorMode, configure_color_mode
except (ImportError, ValueError):
    from color_manager import ColorManager, ColorMode, configure_color_mode


# CRITICAL: Patch Textual Color.parse to accept "default"
_original_color_parse = TextualColor.parse

@classmethod
def _patched_color_parse(cls, color_text: str, *args, **kwargs):
    """Patch Color.parse to accept 'default' keyword"""
    if color_text == "default":
        # Return a marker color that ColorManager will strip
        # Use RGB(0, 0, 1) as marker - nearly invisible but detectable
        return cls(0, 0, 1)
    return _original_color_parse(color_text, *args, **kwargs)

TextualColor.parse = _patched_color_parse


# Patch Textual's Style.rich_style to use ColorManager
from textual.style import Style as TextualStyle

_original_rich_style_func = TextualStyle.rich_style.func

def _patched_textual_rich_style(self):
    """Patch to use ColorManager for background processing"""
    # Get original Rich Style
    color = None if self.foreground is None else self.background + self.foreground

    # Process colors through ColorManager
    processed_color = ColorManager.process_foreground(
        None if color is None else color.rich_color
    )
    processed_bgcolor = ColorManager.process_background(
        None if self.background is None else self.background.rich_color
    )

    return Style(
        color=processed_color,
        bgcolor=processed_bgcolor,
        bold=self.bold,
        dim=self.dim,
        italic=self.italic,
        underline=self.underline,
        underline2=self.underline2,
        reverse=self.reverse,
        strike=self.strike,
        blink=self.blink,
        link=self.link,
        meta=None if self._meta is None else self.meta,
    )

TextualStyle.rich_style.func = _patched_textual_rich_style


# Patch rich_style_with_offset for text selection
_original_rich_style_with_offset = TextualStyle.rich_style_with_offset

def _patched_rich_style_with_offset(self, x: int, y: int):
    """Patch text selection styles to use ColorManager"""
    color = None if self.foreground is None else self.background + self.foreground
    meta = {"offset_x": x, "offset_y": y}
    if self._meta is not None:
        meta.update(self.meta)

    # Process colors through ColorManager
    processed_color = ColorManager.process_foreground(
        None if color is None else color.rich_color
    )
    processed_bgcolor = ColorManager.process_background(
        None if self.background is None else self.background.rich_color
    )

    return Style(
        color=processed_color,
        bgcolor=processed_bgcolor,
        bold=self.bold,
        dim=self.dim,
        italic=self.italic,
        underline=self.underline,
        underline2=self.underline2,
        reverse=self.reverse,
        strike=self.strike,
        blink=self.blink,
        link=self.link,
        meta=meta,
    )

TextualStyle.rich_style_with_offset = _patched_rich_style_with_offset


# Patch DOMNode.rich_style to use ColorManager
from textual.dom import DOMNode

_original_domnode_rich_style = DOMNode.rich_style.fget

def _patched_domnode_rich_style(self):
    """Patch DOMNode.rich_style to use ColorManager"""
    from textual.color import Color

    background = Color(0, 0, 0, 0)
    color = Color(255, 255, 255, 0)
    style = Style()
    opacity = 1.0

    for node in reversed(self.ancestors_with_self):
        styles = node.styles
        has_rule = styles.has_rule
        opacity *= styles.opacity

        if has_rule("background"):
            background = background.blend(styles.background, styles.background.a, alpha=opacity)

        if has_rule("color"):
            color = styles.color

        style += styles.text_style

    # Process colors through ColorManager
    processed_color = ColorManager.process_foreground(color.rich_color)
    processed_bgcolor = ColorManager.process_background(background.rich_color)

    return Style.from_color(processed_color, processed_bgcolor) + style

DOMNode.rich_style = property(_patched_domnode_rich_style)


class ANSIBackgroundMixin:
    """
    Mixin to enable configurable color modes in Textual apps

    Supports:
    - ANSI backgrounds with RGB foregrounds
    - Full RGB (default Textual)
    - Full ANSI 256 colors
    """

    def __init__(self, *args, color_mode: ColorMode = None, **kwargs):
        """
        Initialize with color mode support

        Args:
            color_mode: ColorMode enum value (optional)
        """
        # Set color mode if provided
        if color_mode:
            ColorManager.set_mode(color_mode)

        super().__init__(*args, **kwargs)

    def configure_from_dict(self, config: dict):
        """
        Configure color mode from config dictionary

        Args:
            config: Configuration dictionary
        """
        mode = configure_color_mode(config)
        return mode


def create_ansi_background_app(app_class):
    """
    Decorator to add configurable color mode support to a Textual App

    Usage:
        @create_ansi_background_app
        class MyApp(App):
            ...

        # Then configure:
        app = MyApp()
        app.configure_from_dict(config)
    """

    class ColorModeApp(ANSIBackgroundMixin, app_class):
        """App with configurable color modes"""
        pass

    # Preserve original class name and docs
    ColorModeApp.__name__ = app_class.__name__
    ColorModeApp.__doc__ = app_class.__doc__

    return ColorModeApp


def enable_ansi_backgrounds():
    """
    Global function to enable ANSI background mode

    Call this before starting your Textual app to use
    terminal's native background with RGB foregrounds
    """
    ColorManager.set_mode(ColorMode.ANSI_BG_RGB_FG)


def enable_full_rgb():
    """Enable full RGB mode (Textual default)"""
    ColorManager.set_mode(ColorMode.FULL_RGB)


def enable_full_ansi():
    """Enable full ANSI 256 color mode"""
    ColorManager.set_mode(ColorMode.FULL_ANSI)
