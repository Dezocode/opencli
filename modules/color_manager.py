"""
Color Manager - Configurable dual-mode color system
Supports ANSI backgrounds with RGB foregrounds, full RGB, or full ANSI
"""

from enum import Enum
from typing import Optional
from rich.color import Color as RichColor
from rich.style import Style as RichStyle


class ColorMode(Enum):
    """Color rendering modes"""
    ANSI_BG_RGB_FG = "ansi_bg_rgb_fg"  # ANSI terminal bg, RGB foreground text
    FULL_RGB = "full_rgb"              # Everything RGB (Textual default)
    FULL_ANSI = "full_ansi"            # Everything ANSI 256 colors


class ColorManager:
    """
    Manages color rendering modes for TUI

    Provides configurable dual-mode support:
    - ANSI backgrounds with RGB foregrounds
    - Full RGB colors (default Textual)
    - Full ANSI colors
    """

    _instance = None
    _color_mode = ColorMode.FULL_RGB

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def set_mode(cls, mode: ColorMode):
        """Set global color mode"""
        cls._color_mode = mode

    @classmethod
    def get_mode(cls) -> ColorMode:
        """Get current color mode"""
        return cls._color_mode

    @classmethod
    def should_strip_background(cls) -> bool:
        """Check if backgrounds should be stripped (ANSI mode)"""
        return cls._color_mode == ColorMode.ANSI_BG_RGB_FG

    @classmethod
    def should_force_ansi(cls) -> bool:
        """Check if all colors should be ANSI"""
        return cls._color_mode == ColorMode.FULL_ANSI

    @classmethod
    def process_background(cls, bgcolor: Optional[RichColor]) -> Optional[RichColor]:
        """
        Process background color based on current mode

        Args:
            bgcolor: Rich Color or None

        Returns:
            Processed color or None
        """
        # Check for "default" marker (0, 0, 1) from CSS
        if bgcolor and hasattr(bgcolor, 'triplet') and bgcolor.triplet == (0, 0, 1):
            # This is our "default" marker - always strip
            return None

        if cls._color_mode == ColorMode.ANSI_BG_RGB_FG:
            # Strip all backgrounds - use terminal default
            return None
        elif cls._color_mode == ColorMode.FULL_ANSI and bgcolor:
            # Convert RGB to ANSI 256
            return cls._rgb_to_ansi(bgcolor)
        else:
            # Full RGB - return as-is
            return bgcolor

    @classmethod
    def process_foreground(cls, color: Optional[RichColor]) -> Optional[RichColor]:
        """
        Process foreground color based on current mode

        Args:
            color: Rich Color or None

        Returns:
            Processed color or None
        """
        if cls._color_mode == ColorMode.FULL_ANSI and color:
            # Convert RGB to ANSI 256
            return cls._rgb_to_ansi(color)
        else:
            # RGB modes - return as-is
            return color

    @classmethod
    def create_style(cls, color=None, bgcolor=None, **kwargs) -> RichStyle:
        """
        Create Rich Style with color mode processing

        Args:
            color: Foreground color
            bgcolor: Background color
            **kwargs: Other style attributes

        Returns:
            Rich Style with processed colors
        """
        # Process colors based on mode
        processed_color = cls.process_foreground(color)
        processed_bgcolor = cls.process_background(bgcolor)

        return RichStyle(
            color=processed_color,
            bgcolor=processed_bgcolor,
            **kwargs
        )

    @staticmethod
    def _rgb_to_ansi(rgb_color: RichColor) -> RichColor:
        """Convert RGB color to nearest ANSI 256 color"""
        # Rich automatically handles this with ColorType.EIGHT_BIT
        # We just need to downgrade from TRUECOLOR
        if hasattr(rgb_color, 'triplet'):
            r, g, b = rgb_color.triplet
            # Use Rich's Color.from_rgb which can downgrade
            from rich.color import Color
            ansi_color = Color.from_rgb(r, g, b)
            # Force to 256 color mode
            ansi_color.number  # This downgrades to ANSI automatically
            return ansi_color
        return rgb_color


def configure_color_mode(config: dict):
    """
    Configure color mode from TUI config

    Args:
        config: TUI configuration dictionary
    """
    # Check display.background_mode
    bg_mode = config.get('display', {}).get('background_mode', 'rgb')
    use_ansi = config.get('display', {}).get('use_ansi_colors', False)

    if bg_mode == 'ansi' and use_ansi:
        # ANSI background, RGB foreground
        ColorManager.set_mode(ColorMode.ANSI_BG_RGB_FG)
    elif use_ansi:
        # Full ANSI
        ColorManager.set_mode(ColorMode.FULL_ANSI)
    else:
        # Full RGB (default)
        ColorManager.set_mode(ColorMode.FULL_RGB)

    return ColorManager.get_mode()
