"""
Risk Assessment System for Permission Management
Migrated from modules/tool_permissions.py with enhancements
"""

import json
import os
from pathlib import Path
from enum import Enum
from typing import Tuple, List, Optional, Dict, Any


class RiskLevel(Enum):
    """Risk level classification for operations"""
    SAFE = "safe"           # Read, Glob, Grep - auto-execute
    RISKY = "risky"         # Edit, Write - prompt for confirmation
    DANGEROUS = "dangerous"  # Bash - always prompt with command preview
    CRITICAL = "critical"    # Parent/outside directories, system paths


class RiskAssessmentManager:
    """
    Manages risk assessment for tool operations and file paths
    Provides security-focused evaluation of operations before execution
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.permissions_file = self.config_dir / "tool_permissions.json"
        
        # Tool risk classification
        self.tool_risks = {
            'Read': RiskLevel.SAFE,
            'Glob': RiskLevel.SAFE,
            'Grep': RiskLevel.SAFE,
            'GitHub': RiskLevel.SAFE,
            'Edit': RiskLevel.RISKY,
            'Write': RiskLevel.RISKY,
            'ConfigureHeaders': RiskLevel.RISKY,
            'Bash': RiskLevel.DANGEROUS,
        }
        
        # Load saved permissions
        self.permissions = self._load_permissions()
        
        # Session state
        self.auto_accept_mode = False
        self.accept_all_session = False
    
    def _load_permissions(self) -> Dict[str, Any]:
        """Load tool permissions from file"""
        if not self.permissions_file.exists():
            return {
                'allowed_tools': [],      # Tools always allowed
                'auto_accept': False,     # Global auto-accept mode
            }
        
        try:
            with open(self.permissions_file) as f:
                return json.load(f)
        except Exception:
            return {'allowed_tools': [], 'auto_accept': False}
    
    def _save_permissions(self) -> None:
        """Save permissions to file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.permissions_file, 'w') as f:
                json.dump(self.permissions, f, indent=2)
        except Exception as e:
            import sys
            sys.stderr.write(f"⚠️  Could not save permissions: {e}\n")
            sys.stderr.flush()
    
    def get_tool_risk(self, tool_name: str) -> RiskLevel:
        """Get the risk level for a specific tool"""
        return self.tool_risks.get(tool_name, RiskLevel.RISKY)
    
    def assess_path_risk(self, file_path: str, current_dir: Optional[str] = None) -> Tuple[RiskLevel, str]:
        """
        Assess risk level of file path
        
        Returns: (risk_level: RiskLevel, reason: str)
        """
        if not file_path:
            return RiskLevel.SAFE, "no path specified"
        
        # Get current working directory
        cwd = Path(current_dir or os.getcwd()).resolve()
        
        try:
            target = Path(file_path).resolve()
        except Exception as e:
            return RiskLevel.RISKY, f"invalid path: {e}"
        
        # Critical paths (system directories)
        critical_paths = [
            Path('/etc').resolve(),          # Resolve symlinks (macOS: /etc -> /private/etc)
            Path('/private/etc'),
            Path('/bin').resolve(),
            Path('/sbin').resolve(),
            Path('/usr/bin'),
            Path('/usr/sbin'),
            Path('/System'),
            Path('/Library'),
            Path('/var'),
            Path.home() / '.ssh',
            Path.home() / '.aws',
            Path.home() / '.config',
        ]
        
        # Check if target is in critical system path
        for critical in critical_paths:
            try:
                if target.is_relative_to(critical):
                    return RiskLevel.CRITICAL, f"system directory: {critical}"
            except (ValueError, AttributeError):
                # is_relative_to not available in older Python
                try:
                    target.relative_to(critical)
                    return RiskLevel.CRITICAL, f"system directory: {critical}"
                except ValueError:
                    pass
        
        # Check if target is outside current directory
        try:
            target.relative_to(cwd)
            # Within current directory
            return RiskLevel.SAFE, "within working directory"
        except ValueError:
            # Outside current directory
            # Check if it's a parent directory
            try:
                cwd.relative_to(target)
                return RiskLevel.DANGEROUS, f"parent directory: {target}"
            except ValueError:
                return RiskLevel.DANGEROUS, f"outside working directory: {target}"
    
    def assess_operation_risk(
        self, 
        tool_name: str, 
        args: Optional[Dict[str, Any]] = None, 
        current_dir: Optional[str] = None
    ) -> Tuple[RiskLevel, str]:
        """
        Assess overall risk level for an operation
        Considers both tool risk and path risk
        
        Returns: (risk_level: RiskLevel, reason: str)
        """
        # Get tool risk
        tool_risk = self.get_tool_risk(tool_name)
        
        # Assess path risk for file operations
        path_risk = RiskLevel.SAFE
        path_reason = ""
        
        if args and tool_name in ['Edit', 'Write', 'Read']:
            file_path = args.get('file_path')
            if file_path:
                path_risk, path_reason = self.assess_path_risk(file_path, current_dir)
        
        # Use higher of tool_risk and path_risk
        risk_levels = {
            RiskLevel.SAFE: 0,
            RiskLevel.RISKY: 1,
            RiskLevel.DANGEROUS: 2,
            RiskLevel.CRITICAL: 3
        }
        
        if risk_levels[path_risk] > risk_levels[tool_risk]:
            return path_risk, path_reason
        else:
            return tool_risk, f"{tool_risk.value} tool"
    
    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check if tool is in allowed list"""
        return tool_name in self.permissions.get('allowed_tools', [])
    
    def add_allowed_tool(self, tool_name: str) -> bool:
        """Add tool to allowed list (skip future prompts)"""
        if tool_name not in self.permissions.get('allowed_tools', []):
            if 'allowed_tools' not in self.permissions:
                self.permissions['allowed_tools'] = []
            self.permissions['allowed_tools'].append(tool_name)
            self._save_permissions()
            return True
        return False
    
    def remove_allowed_tool(self, tool_name: str) -> bool:
        """Remove tool from allowed list"""
        if tool_name in self.permissions.get('allowed_tools', []):
            self.permissions['allowed_tools'].remove(tool_name)
            self._save_permissions()
            return True
        return False
    
    def set_auto_accept(self, enabled: bool) -> None:
        """Enable/disable global auto-accept mode"""
        self.permissions['auto_accept'] = enabled
        self.auto_accept_mode = enabled
        self._save_permissions()
    
    def should_prompt(
        self, 
        tool_name: str, 
        args: Optional[Dict[str, Any]] = None, 
        current_dir: Optional[str] = None
    ) -> Tuple[bool, str, RiskLevel]:
        """
        Determine if we should prompt for permission
        
        Returns: (should_prompt: bool, reason: str, risk_level: RiskLevel)
        """
        # Assess operation risk
        risk_level, risk_reason = self.assess_operation_risk(tool_name, args, current_dir)
        
        # CRITICAL operations always require prompt
        if risk_level == RiskLevel.CRITICAL:
            return True, f"CRITICAL: {risk_reason}", risk_level
        
        # Check if in auto-accept mode (global or session)
        if self.auto_accept_mode or self.accept_all_session:
            # Don't auto-accept DANGEROUS operations
            if risk_level == RiskLevel.DANGEROUS:
                return True, f"dangerous operation: {risk_reason}", risk_level
            return False, "auto-accept enabled", risk_level
        
        # Check global auto-accept from config
        if self.permissions.get('auto_accept', False):
            # Don't auto-accept DANGEROUS operations
            if risk_level == RiskLevel.DANGEROUS:
                return True, f"dangerous operation: {risk_reason}", risk_level
            return False, "global auto-accept", risk_level
        
        # Check if tool is in allowed list
        if self.is_tool_allowed(tool_name):
            # Don't auto-allow DANGEROUS operations
            if risk_level == RiskLevel.DANGEROUS:
                return True, f"dangerous operation: {risk_reason}", risk_level
            return False, "tool allowed", risk_level
        
        # SAFE tools don't require prompt (unless path is risky)
        if risk_level == RiskLevel.SAFE:
            return False, "safe operation", risk_level
        
        # Risky and dangerous tools require prompt
        return True, f"{risk_level.value} operation", risk_level
    
    def format_operation_preview(
        self, 
        tool_name: str, 
        args: Dict[str, Any], 
        current_dir: Optional[str] = None
    ) -> str:
        """Format tool operation for preview in permission prompt"""
        preview_lines = []
        
        if tool_name == 'Edit':
            file_path = args.get('file_path', 'unknown')
            old_str = args.get('old_string', '')[:50]
            new_str = args.get('new_string', '')[:50]
            preview_lines.append(f"**File:** `{file_path}`")
            preview_lines.append(f"**Replace:** {old_str}...")
            preview_lines.append(f"**With:** {new_str}...")
        
        elif tool_name == 'Write':
            file_path = args.get('file_path', 'unknown')
            content = args.get('content', '')
            content_preview = content[:100]
            preview_lines.append(f"**File:** `{file_path}`")
            preview_lines.append(f"**Content:** ({len(content)} chars)")
            preview_lines.append(f"```\n{content_preview}...\n```")
        
        elif tool_name == 'Read':
            file_path = args.get('file_path', 'unknown')
            preview_lines.append(f"**File:** `{file_path}`")
        
        elif tool_name == 'Bash':
            command = args.get('command', 'unknown')
            description = args.get('description', 'No description')
            preview_lines.append(f"**Command:** `{command}`")
            preview_lines.append(f"**Description:** {description}")
        
        else:
            preview_lines.append(f"**Tool:** {tool_name}")
            for key, value in args.items():
                preview_lines.append(f"**{key}:** {value}")
        
        # Add path risk warning if applicable
        if tool_name in ['Edit', 'Write', 'Read']:
            file_path = args.get('file_path')
            if file_path:
                path_risk_level, path_reason = self.assess_path_risk(file_path, current_dir)
                if path_risk_level in [RiskLevel.DANGEROUS, RiskLevel.CRITICAL]:
                    cwd = Path(current_dir or os.getcwd()).resolve()
                    preview_lines.append("\n⚠️ **PATH WARNING**")
                    preview_lines.append(f"- {path_reason}")
                    preview_lines.append(f"- Current directory: `{cwd}`")
                    preview_lines.append(f"- Target path: `{Path(file_path).resolve()}`")
        
        return "\n".join(preview_lines)
    
    def get_allowed_tools(self) -> List[str]:
        """Get list of allowed tools"""
        return self.permissions.get('allowed_tools', [])
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get summary of risk assessment configuration"""
        return {
            'auto_accept_mode': self.auto_accept_mode or self.permissions.get('auto_accept', False),
            'session_accept_all': self.accept_all_session,
            'allowed_tools': self.get_allowed_tools(),
            'tool_risks': {tool: risk.value for tool, risk in self.tool_risks.items()},
            'permissions_file': str(self.permissions_file)
        }


# Global instance
_global_risk_manager: Optional[RiskAssessmentManager] = None


def get_risk_assessment_manager() -> RiskAssessmentManager:
    """Get the global risk assessment manager instance"""
    global _global_risk_manager
    if _global_risk_manager is None:
        _global_risk_manager = RiskAssessmentManager()
    return _global_risk_manager
