# OpenCLI TUI Configuration Guide

Complete guide for customizing the OpenCLI Terminal User Interface.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Text Selection](#text-selection)
3. [Laser Effect](#laser-effect)
4. [Background & Colors](#background--colors)
5. [Mouse Behavior](#mouse-behavior)
6. [Configuration File](#configuration-file)
7. [Slash Commands](#slash-commands)

---

## Quick Start

### View Current Configuration

```bash
/tui
```

Shows your complete TUI configuration in JSON format.

### Get Help

```bash
/tui help
```

---

## Text Selection

OpenCLI supports two text selection modes:

### Native Mode (Default)

Uses your terminal's built-in selection with a modifier key.

**Activate:**
```bash
/tui selection native
```

**How to select text:**
- **macOS (iTerm)**: Hold **OPTION** + drag
- **Linux/Windows**: Hold **SHIFT** + drag
- Then **Cmd+C** or **Ctrl+C** to copy

### Custom Mode

Click-and-drag selection without modifier keys.

**Activate:**
```bash
/tui selection custom
```

**How to select text:**
- **Click and drag** to select
- Text is automatically copied to clipboard on mouse release

**Note:** Custom mode requires `pyperclip` package:
```bash
pip install pyperclip
```

---

## Laser Effect

The hot laser effect creates an animated color gradient as text streams in.

### Enable/Disable

```bash
/tui laser on
/tui laser off
```

### Modes

**Gradient Mode (Default)**
Smooth transition from dark red → orange → yellow → white
```bash
/tui laser mode gradient
```

**Pulse Mode**
Alternating red/white pulsing effect
```bash
/tui laser mode pulse
```

**Trail Mode**
Orange trail with bright white hotspot
```bash
/tui laser mode trail
```

### Intensity

Control brightness (0.0 to 1.0):

```bash
/tui laser intensity 1.0    # Full brightness (bold)
/tui laser intensity 0.5    # Medium brightness
/tui laser intensity 0.2    # Subtle effect
```

### Custom Colors

Edit `~/.opencli/tui_config.json`:

```json
{
  "laser_effect": {
    "enabled": true,
    "mode": "gradient",
    "colors": {
      "gradient": ["#8B0000", "#FF4500", "#FFA500", "#FFFF00", "#FFFFFF"],
      "custom": ["#0000FF", "#00FFFF", "#FFFFFF"]
    }
  }
}
```

Then:
```bash
/tui laser mode custom
```

---

## Background & Colors

### Theme Mode (Default)

Uses Textual's built-in dark theme background.

```bash
/tui background theme
```

**Pros:**
- Rich color support (16.7M colors)
- Advanced effects and gradients
- Consistent across terminals

**Cons:**
- Dark gray background (not transparent)

### ANSI Mode

Uses terminal's native ANSI background colors.

```bash
/tui background ansi
```

**Pros:**
- Respects terminal transparency
- Native terminal theme support

**Cons:**
- Limited color palette
- Loses some visual effects

---

## Mouse Behavior

Configure mouse interactions:

### Disable Mouse Capture

Allow terminal's native mouse handling:

```json
{
  "mouse": {
    "enabled": true,
    "capture": false,
    "selection_enabled": true
  }
}
```

### Double/Triple Click

```json
{
  "mouse": {
    "double_click_select_word": true,
    "triple_click_select_line": true
  }
}
```

---

## Configuration File

Location: `~/.opencli/tui_config.json`

### Full Configuration Schema

```json
{
  "version": "1.0.0",
  "display": {
    "background_mode": "theme",
    "use_ansi_colors": false,
    "dark_mode": false,
    "transparency": {
      "enabled": true,
      "opacity": 0.95
    }
  },
  "text_selection": {
    "mode": "native",
    "require_modifier": false,
    "copy_on_select": false,
    "highlight_color": "#3A3A3A"
  },
  "laser_effect": {
    "enabled": true,
    "mode": "gradient",
    "colors": {
      "gradient": ["#8B0000", "#FF4500", "#FFA500", "#FFFF00", "#FFFFFF"],
      "pulse": ["#FF0000", "#FFFFFF"],
      "trail": ["#FF6600", "#FFAA00", "#FFDD00", "#FFFFFF"]
    },
    "intensity": 1.0,
    "speed": 1.0,
    "trail_length": 10
  },
  "mouse": {
    "enabled": true,
    "capture": false,
    "selection_enabled": true,
    "double_click_select_word": true,
    "triple_click_select_line": true
  },
  "scrolling": {
    "smooth": true,
    "speed": 3,
    "mouse_wheel_enabled": true
  },
  "borders": {
    "style": "solid",
    "color": "#888888",
    "content_border": true,
    "footer_border": false
  },
  "status_bar": {
    "enabled": true,
    "show_model": true,
    "show_tokens": true,
    "show_turn": true,
    "show_cwd": true,
    "show_time": true,
    "update_interval": 1.0
  },
  "prompt": {
    "style": "rich",
    "color": "#00FF00",
    "indicator": "│ > ",
    "placeholder": "Enter your message..."
  },
  "animations": {
    "enabled": true,
    "fade_in": false,
    "smooth_scroll": true
  }
}
```

---

## Slash Commands

### Basic Commands

```bash
# Show config
/tui

# Get help
/tui help

# Get specific value
/tui get laser_effect.enabled

# Set specific value
/tui set laser_effect.intensity 0.8
```

### Laser Effect

```bash
# Toggle
/tui laser on
/tui laser off

# Change mode
/tui laser mode gradient
/tui laser mode pulse
/tui laser mode trail

# Adjust intensity
/tui laser intensity 0.5
```

### Text Selection

```bash
# Native (Shift+drag)
/tui selection native

# Custom (click+drag)
/tui selection custom
```

### Background

```bash
# Textual theme
/tui background theme

# Terminal ANSI
/tui background ansi
```

### Utilities

```bash
# Reset to defaults
/tui reset

# Reload from file
/tui reload
```

---

## Recommended Configurations

### Maximum Visual Impact

```bash
/tui laser on
/tui laser mode gradient
/tui laser intensity 1.0
/tui background theme
```

### Minimal/Transparent

```bash
/tui laser off
/tui background ansi
/tui selection native
```

### Easy Selection

```bash
/tui selection custom
/tui laser on
/tui laser intensity 0.5
```

---

## Troubleshooting

### Text Selection Not Working

**Problem:** Can't select text in the TUI

**Solution:**
1. Use native mode: `/tui selection native`
2. Hold **SHIFT** (or **OPTION** on macOS) while dragging
3. Or enable custom mode: `/tui selection custom`

### Laser Effect Too Bright

**Problem:** Streaming text is too intense

**Solution:**
```bash
/tui laser intensity 0.3
```

### Background Still Dark

**Problem:** Background won't become transparent

**Solution:**
Textual's theme mode uses a solid background. Switch to ANSI:
```bash
/tui background ansi
```

**Note:** This disables some rich color features.

### Config Changes Not Applied

**Problem:** Settings changed but nothing happens

**Solution:**
Restart OpenCLI after configuration changes:
```bash
exit
opencli
```

---

## Advanced: Manual Editing

Edit `~/.opencli/tui_config.json` directly for advanced customization.

After editing, reload:
```bash
/tui reload
```

Or restart OpenCLI.

---

## Support

For issues or feature requests, check:
- GitHub: https://github.com/yourusername/opencli
- Documentation: `~/.opencli/TUI_GUIDE.md`
