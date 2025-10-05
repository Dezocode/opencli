"""Minimal TUI configuration support for OpenCLI Textual front-end."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class TUIConfig:
    """Runtime configuration values consumed by the Textual UI."""

    config: Dict[str, Any] = field(default_factory=lambda: {
        "display": {
            "background_mode": "ansi",
            "use_ansi_colors": True,
        },
        "text_selection": {
            "mode": "default",
        },
    })
    laser_enabled: bool = True
    laser_colors: List[str] = field(default_factory=lambda: [
        "#8B0000",
        "#FF4500",
        "#FFA500",
        "#FFFF00",
        "#FFFFFF",
    ])
    laser_intensity: float = 1.0

    def get(self, path: str, default: Any = None) -> Any:
        """Utility helper to fetch nested configuration values."""
        parts = path.split(".")
        data: Any = self.config
        for part in parts:
            if isinstance(data, dict) and part in data:
                data = data[part]
            else:
                return default
        return data


def get_tui_config() -> TUIConfig:
    """Return the singleton TUI configuration object."""
    return TUIConfig()
