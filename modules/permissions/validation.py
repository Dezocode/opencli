"""
Validation logic for permission system
Prompt data validation, response validation, color format checking
"""

import re
from typing import Dict, List, Optional, Any, Tuple


class ValidationManager:
    """Handles validation for permission prompts (Constitution compliant security)"""
    
    def __init__(self):
        # Color format validation regex
        self._hex_color_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        self._rgb_color_pattern = re.compile(r'^rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)$')
        
    def validate_prompt_data(self, prompt_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate permission prompt data (Constitution compliant security)
        
        Returns (is_valid, error_message)
        """
        if not isinstance(prompt_data, dict):
            return False, "Prompt data must be a dictionary"
        
        # Required fields validation
        title = prompt_data.get('title')
        if not title or not isinstance(title, str) or not title.strip():
            return False, "Title is required and must be a non-empty string"
        
        # Title length validation
        if len(title) > 200:
            return False, "Title must be 200 characters or less"
        
        # Message validation (optional but if present must be valid)
        message = prompt_data.get('message')
        if message is not None:
            if not isinstance(message, str):
                return False, "Message must be a string"
            if len(message) > 2000:
                return False, "Message must be 2000 characters or less"
        
        # Options validation
        options = prompt_data.get('options', [])
        if not isinstance(options, list):
            return False, "Options must be a list"
        
        if len(options) > 20:
            return False, "Cannot have more than 20 options"
        
        for i, option in enumerate(options):
            if not isinstance(option, dict):
                return False, f"Option {i+1} must be a dictionary"

            # Option label validation - accept both 'label' and 'text' for backwards compatibility
            label = option.get('label') or option.get('text')
            if not label or not isinstance(label, str) or not label.strip():
                return False, f"Option {i+1} must have a non-empty label or text"

            if len(label) > 100:
                return False, f"Option {i+1} label must be 100 characters or less"
            
            # Option value validation (optional)
            value = option.get('value')
            if value is not None and not isinstance(value, (str, int, float, bool)):
                return False, f"Option {i+1} value must be a string, number, or boolean"
            
            # Color validation (optional)
            color = option.get('color')
            if color is not None:
                is_valid_color, color_error = self._validate_color_format(color)
                if not is_valid_color:
                    return False, f"Option {i+1} color: {color_error}"
        
        # Default option validation
        default_option = prompt_data.get('default_option')
        if default_option is not None:
            if not isinstance(default_option, int):
                return False, "Default option must be an integer index"
            if default_option < 0 or default_option >= len(options):
                return False, "Default option index is out of range"
        
        # Auto-dismiss timeout validation
        auto_dismiss_timeout = prompt_data.get('auto_dismiss_timeout')
        if auto_dismiss_timeout is not None:
            if not isinstance(auto_dismiss_timeout, (int, float)):
                return False, "Auto-dismiss timeout must be a number"
            if auto_dismiss_timeout <= 0:
                return False, "Auto-dismiss timeout must be positive"
            if auto_dismiss_timeout > 300:
                return False, "Auto-dismiss timeout cannot exceed 300 seconds"
        
        return True, None

    def _validate_color_format(self, color: str) -> Tuple[bool, Optional[str]]:
        """Validate color format (Constitution compliant)
        
        Supports:
        - Hex colors: #RRGGBB
        - RGB colors: rgb(r, g, b)
        - Named colors: common CSS color names
        
        Returns (is_valid, error_message)
        """
        if not isinstance(color, str):
            return False, "Color must be a string"
        
        color = color.strip()
        
        # Hex color validation
        if color.startswith('#'):
            if self._hex_color_pattern.match(color):
                return True, None
            else:
                return False, "Invalid hex color format. Use #RRGGBB"
        
        # RGB color validation
        if color.startswith('rgb('):
            if self._rgb_color_pattern.match(color):
                # Extract RGB values and validate range
                rgb_part = color[4:-1]  # Remove 'rgb(' and ')'
                rgb_values = [int(x.strip()) for x in rgb_part.split(',')]
                for value in rgb_values:
                    if value < 0 or value > 255:
                        return False, "RGB values must be between 0 and 255"
                return True, None
            else:
                return False, "Invalid RGB color format. Use rgb(r, g, b)"
        
        # Named color validation (basic CSS colors)
        named_colors = {
            'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
            'orange', 'purple', 'pink', 'brown', 'gray', 'grey', 'lime', 'navy',
            'olive', 'silver', 'teal', 'maroon', 'aqua', 'fuchsia'
        }
        
        if color.lower() in named_colors:
            return True, None
        
        return False, "Unsupported color format. Use hex (#RRGGBB), RGB (rgb(r,g,b)), or named colors"

    def validate_prompt_response(self, response: Dict[str, Any], original_options: List[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        """Validate permission prompt response (Constitution compliant security)
        
        Returns (is_valid, error_message)
        """
        if not isinstance(response, dict):
            return False, "Response must be a dictionary"
        
        # Selected option validation
        selected = response.get('selected')
        if selected is None:
            return False, "Response must include 'selected' field"
        
        if not isinstance(selected, int):
            return False, "Selected option must be an integer"
        
        # Validate against original options if provided
        if original_options is not None:
            if selected < 0 or selected >= len(original_options):
                return False, f"Selected option {selected} is out of range (0-{len(original_options)-1})"
        
        # Remember choice validation (optional)
        remember = response.get('remember')
        if remember is not None and not isinstance(remember, bool):
            return False, "Remember choice must be a boolean"
        
        # Custom data validation (optional)
        custom_data = response.get('custom_data')
        if custom_data is not None:
            if not isinstance(custom_data, dict):
                return False, "Custom data must be a dictionary"
            
            # Basic size limit for custom data
            import json
            try:
                custom_json = json.dumps(custom_data)
                if len(custom_json) > 1000:
                    return False, "Custom data exceeds size limit (1000 characters)"
            except (TypeError, ValueError):
                return False, "Custom data must be JSON serializable"
        
        return True, None
    
    def validate_task_id(self, task_id: str) -> bool:
        """Validate task ID format"""
        if not isinstance(task_id, str):
            return False
        
        # Check length (UUID is 36 chars)
        if len(task_id) < 8 or len(task_id) > 50:
            return False
        
        # Check for invalid characters
        valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if not all(c in valid_chars for c in task_id):
            return False
        
        return True
    
    def validate_priority_value(self, priority: Any) -> bool:
        """Validate priority enum value"""
        from .enums import PromptPriority
        
        if isinstance(priority, PromptPriority):
            return True
        
        if isinstance(priority, str):
            return priority.upper() in [p.name for p in PromptPriority]
        
        if isinstance(priority, int):
            return priority in [p.value for p in PromptPriority]
        
        return False
    
    def sanitize_string(self, text: str, max_length: int = 1000) -> str:
        """Sanitize string input for security"""
        if not isinstance(text, str):
            return ""
        
        # Remove control characters except newlines and tabs
        sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Truncate to max length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length-3] + "..."
        
        return sanitized