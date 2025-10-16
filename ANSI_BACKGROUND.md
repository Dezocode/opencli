# ANSI Background Support

## We Built It! 🔥

You were right - it IS possible to use ANSI terminal backgrounds while keeping rich text colors. We're builders, and here's how we did it:

## How It Works

### 1. **Custom Mixin Class** (`ansi_background.py`)

Created `ANSIBackgroundMixin` that:
- Intercepts CSS variable resolution
- Overrides only background-related variables to use `ansi_default`
- Keeps all foreground color variables intact for rich text support

### 2. **Decorator Pattern**

```python
@create_ansi_background_app
class OpenCLITUI(App):
    ...
```

The decorator adds ANSI background support without modifying the base class.

### 3. **Selective Override**

When `ansi_background=True`:
```python
ansi_overrides = {
    "$background": "ansi_default",  # Use terminal background
    "$surface": "ansi_default",      # Use terminal background
    "$panel": "ansi_default",        # Use terminal background
    "$boost": "ansi_default",        # Use terminal background
}
```

All other CSS variables (text colors, borders, etc.) remain rich colors!

## Usage

### Enable ANSI Background

```bash
/tui background ansi
```

This sets:
```json
{
  "display": {
    "background_mode": "ansi",
    "use_ansi_colors": true
  }
}
```

### Disable (Use Rich Theme)

```bash
/tui background theme
```

## What You Get

### ✅ With ANSI Background Mode

- **Terminal-native background** (respects transparency/theme)
- **Full rich text colors** (16.7M colors for text)
- **Laser effect works perfectly** (rich gradient colors)
- **Native terminal feel**

### ❌ What You Lose

- Textual's background gradients/effects (not needed!)
- Consistent background across all terminals (you want native anyway!)

## Technical Details

### The Secret Sauce

Textual uses CSS variables like `$background` that map to color values. By intercepting `get_css_variables()` and only overriding background-related variables to `ansi_default`, we get:

1. **Terminal's ANSI background** - Native, transparent, themed
2. **Rich foreground colors** - Full 16.7M color palette for text

### Why This Works

- Background and foreground rendering are separate in terminal emulators
- ANSI escape codes: `\033[48;...m` (background) vs `\033[38;...m` (foreground)
- We use ANSI for background, rich RGB codes for foreground
- Terminal emulators support mixing both!

## Configuration

### Via TUI Config File

Edit `~/.opencli/tui_config.json`:

```json
{
  "display": {
    "background_mode": "ansi",
    "use_ansi_colors": true
  }
}
```

### Via Command

```bash
/tui background ansi
```

## Architecture

```
OpenCLITUI (base class)
    ↓
ANSIBackgroundMixin.get_css_variables()
    ↓
Override $background, $surface, $panel, $boost → "ansi_default"
    ↓
Keep all other variables → Rich RGB colors
    ↓
Terminal Rendering:
  - Background: ANSI default (transparent/native)
  - Text: Rich RGB colors (laser effect, gradients, etc.)
```

## Testing

1. **Enable ANSI background:**
   ```bash
   /tui background ansi
   ```

2. **Restart OpenCLI:**
   ```bash
   exit
   opencli
   ```

3. **Verify:**
   - Background matches your terminal's native background
   - Laser effect still works with rich colors
   - Text has full color support

## Troubleshooting

### Background Still Dark?

Make sure config is saved:
```bash
/tui get display.use_ansi_colors
```

Should return `true`.

### Laser Effect Not Working?

The laser effect uses rich foreground colors, which work independently:
```bash
/tui laser on
/tui get laser_effect.enabled
```

## The Builder's Way

Instead of accepting "it's not possible," we:

1. ✅ Read the Textual source code
2. ✅ Understood the CSS variable system
3. ✅ Created a mixin to override only what we need
4. ✅ Applied decorator pattern for clean integration
5. ✅ Made it configurable via TUI config
6. ✅ Documented everything

**We're builders. We make it work.** 🛠️

## Credits

Built because you challenged us to do it right.
Open source means we can fix anything.
