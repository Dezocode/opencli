# OpenCLI Color Modes

Configurable dual-mode color system supporting ANSI backgrounds with RGB foregrounds, full RGB, or full ANSI.

## Architecture

### ColorManager (`color_manager.py`)
Central singleton managing color mode state and processing all colors before rendering.

### Color Modes

#### 1. ANSI_BG_RGB_FG (Recommended)
**Config:**
```json
{
  "display": {
    "background_mode": "ansi",
    "use_ansi_colors": true
  }
}
```

**Behavior:**
- **Backgrounds:** Stripped - terminal's native ANSI background shows through
- **Foregrounds:** Full RGB (16.7M colors) for text, laser effects, all UI elements
- **Use case:** Transparent terminals, terminal background images, custom ANSI themes

**Benefits:**
- Terminal transparency works
- Custom terminal backgrounds visible
- Full RGB color for rich effects
- Laser effects work perfectly

---

#### 2. FULL_RGB (Textual Default)
**Config:**
```json
{
  "display": {
    "background_mode": "rgb",
    "use_ansi_colors": false
  }
}
```

**Behavior:**
- **Backgrounds:** Full RGB colors
- **Foregrounds:** Full RGB colors
- **Use case:** Standard Textual TUI, no transparency needed

**Benefits:**
- Maximum color control
- Textual default behavior
- Works on all terminals

---

#### 3. FULL_ANSI
**Config:**
```json
{
  "display": {
    "background_mode": "rgb",
    "use_ansi_colors": true
  }
}
```

**Behavior:**
- **Backgrounds:** ANSI 256 colors
- **Foregrounds:** ANSI 256 colors
- **Use case:** Limited color terminals, retro aesthetics

**Benefits:**
- Works on older terminals
- Consistent across terminal types
- Smaller color palette

---

## Implementation Details

### Patching Strategy

The system patches Textual at THREE critical conversion points:

1. **TextualStyle.rich_style** (`textual/style.py:346`)
   - Converts Textual Style objects to Rich Styles
   - ColorManager processes colors BEFORE Rich Style creation

2. **TextualStyle.rich_style_with_offset** (`textual/style.py:368`)
   - Used for text selection rendering
   - Also processes through ColorManager

3. **DOMNode.rich_style** (`textual/dom.py:1064`)
   - Builds Rich Styles from CSS/DOM tree
   - ColorManager processes final computed colors

### Color Processing Flow

```
Textual CSS → Textual Color → ColorManager → Rich Color → Rich Style → Terminal
                                    ↑
                              Mode-based processing
```

**ANSI_BG_RGB_FG mode:**
```python
# Background colors
process_background(color) → None  # Stripped

# Foreground colors
process_foreground(color) → color  # Preserved RGB
```

**FULL_RGB mode:**
```python
# All colors
process_**(color) → color  # Preserved as-is
```

**FULL_ANSI mode:**
```python
# All colors
process_**(color) → rgb_to_ansi(color)  # Downgrade to ANSI 256
```

---

## Usage

### In TUI Application

```python
from modules.simple_tui import OpenCLITUI
from modules.tui_config import get_tui_config

# Load config - color mode auto-configured
config = get_tui_config()

# TUI __init__ calls configure_color_mode() automatically
app = OpenCLITUI(session, config)
```

### Manual Configuration

```python
from modules.color_manager import ColorManager, ColorMode

# Set mode directly
ColorManager.set_mode(ColorMode.ANSI_BG_RGB_FG)

# Or configure from dict
from modules.color_manager import configure_color_mode

config = {
    "display": {
        "background_mode": "ansi",
        "use_ansi_colors": True
    }
}

mode = configure_color_mode(config)
```

### Helper Functions

```python
from modules.ansi_background import (
    enable_ansi_backgrounds,  # ANSI_BG_RGB_FG
    enable_full_rgb,          # FULL_RGB
    enable_full_ansi          # FULL_ANSI
)

# Call before starting app
enable_ansi_backgrounds()
```

---

## Configuration Reference

### tui_config.json

```json
{
  "display": {
    "background_mode": "ansi|rgb",
    "use_ansi_colors": true|false,
    "dark_mode": false
  }
}
```

**Mode Selection Logic:**

| background_mode | use_ansi_colors | Result         |
|----------------|-----------------|----------------|
| "ansi"         | true            | ANSI_BG_RGB_FG |
| "ansi"         | false           | FULL_RGB       |
| "rgb"          | true            | FULL_ANSI      |
| "rgb"          | false           | FULL_RGB       |

---

## Testing

```python
from modules.color_manager import ColorManager, ColorMode
from rich.color import Color

# Configure mode
ColorManager.set_mode(ColorMode.ANSI_BG_RGB_FG)

# Test processing
test_bg = Color.parse('#FF0000')
test_fg = Color.parse('#00FF00')

processed_bg = ColorManager.process_background(test_bg)
processed_fg = ColorManager.process_foreground(test_fg)

assert processed_bg is None  # Background stripped
assert processed_fg == test_fg  # Foreground preserved
```

---

## Terminal Compatibility

### ANSI_BG_RGB_FG Mode
✅ Ghostty (transparency + RGB)
✅ iTerm2 (transparency + RGB)
✅ Alacritty (transparency + RGB)
✅ WezTerm (transparency + RGB)
✅ Kitty (transparency + RGB)
⚠️ Terminal.app (RGB only, no true transparency)

### FULL_RGB Mode
✅ All modern terminals

### FULL_ANSI Mode
✅ All terminals (256 color minimum)

---

## Troubleshooting

**Black background still showing:**
1. Check config: `background_mode` should be `"ansi"`
2. Check config: `use_ansi_colors` should be `true`
3. Verify mode: Should print `🎨 Color mode: ansi_bg_rgb_fg` on startup
4. Check terminal: Must support transparency/ANSI backgrounds

**Colors look wrong:**
1. Verify ColorManager mode with `ColorManager.get_mode()`
2. Check terminal color support
3. Try different mode in config

**Laser effects not working:**
1. Laser uses RGB colors - works in ANSI_BG_RGB_FG and FULL_RGB
2. Check `laser_effect.enabled` in config
3. Verify laser colors are valid hex codes
