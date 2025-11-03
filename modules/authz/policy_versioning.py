"""
Policy Versioning System - Phase 3

Enables safe policy updates with:
- Version tracking
- Rollback capability
- Canary deployments
- A/B testing

Usage:
    from modules.authz.policy_versioning import get_policy_manager
    
    manager = get_policy_manager()
    manager.set_policy_version("2.0.0")
    manager.enable_canary("2.0.0", percentage=10)
"""

import json
import random
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PolicyVersion:
    """Policy version metadata"""
    version: str
    description: str
    created_at: str
    active: bool = False
    canary_percentage: float = 0.0  # 0-100
    rollback_safe: bool = True


class PolicyVersionManager:
    """Manage policy versions for authorization system"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.policy_file = self.config_dir / "policy_versions.json"
        self._lock = threading.Lock()
        
        # Policy versions registry
        self._versions: Dict[str, PolicyVersion] = {}
        self._current_version = "1.0.0"
        
        # Load saved policies
        self._load_policies()
        
        # Ensure default policy exists
        if "1.0.0" not in self._versions:
            self.register_policy_version(
                "1.0.0",
                "Initial policy version",
                active=True
            )
    
    def register_policy_version(
        self,
        version: str,
        description: str,
        active: bool = False
    ) -> bool:
        """Register a new policy version"""
        with self._lock:
            if version in self._versions:
                return False
            
            policy = PolicyVersion(
                version=version,
                description=description,
                created_at=datetime.now().isoformat(),
                active=active
            )
            
            self._versions[version] = policy
            
            if active:
                self._current_version = version
            
            self._save_policies()
            return True
    
    def set_policy_version(self, version: str) -> bool:
        """Set active policy version"""
        with self._lock:
            if version not in self._versions:
                return False
            
            # Deactivate all
            for v in self._versions.values():
                v.active = False
                v.canary_percentage = 0.0
            
            # Activate target
            self._versions[version].active = True
            self._current_version = version
            
            self._save_policies()
            return True
    
    def enable_canary(
        self,
        version: str,
        percentage: float
    ) -> bool:
        """
        Enable canary deployment for a version
        
        Args:
            version: Policy version to canary test
            percentage: Percentage of traffic (0-100)
        
        Returns:
            True if successful
        """
        with self._lock:
            if version not in self._versions:
                return False
            
            if not 0 <= percentage <= 100:
                return False
            
            self._versions[version].canary_percentage = percentage
            self._save_policies()
            return True
    
    def get_policy_version_for_request(self) -> str:
        """
        Get policy version for this request (considers canary)
        
        Returns:
            Version string to use
        """
        with self._lock:
            # Check if any canary deployments active
            canary_versions = [
                v for v in self._versions.values()
                if v.canary_percentage > 0
            ]
            
            if canary_versions:
                # Randomly select based on canary percentage
                roll = random.random() * 100
                
                for canary in canary_versions:
                    if roll < canary.canary_percentage:
                        return canary.version
            
            # Default to current version
            return self._current_version
    
    def get_current_version(self) -> str:
        """Get currently active policy version"""
        with self._lock:
            return self._current_version
    
    def list_versions(self) -> Dict[str, PolicyVersion]:
        """List all registered policy versions"""
        with self._lock:
            return dict(self._versions)
    
    def rollback_to_version(self, version: str) -> bool:
        """Rollback to a previous policy version"""
        with self._lock:
            if version not in self._versions:
                return False
            
            policy = self._versions[version]
            if not policy.rollback_safe:
                return False
            
            return self.set_policy_version(version)
    
    def mark_version_unsafe(self, version: str) -> bool:
        """Mark a version as unsafe for rollback"""
        with self._lock:
            if version not in self._versions:
                return False
            
            self._versions[version].rollback_safe = False
            self._save_policies()
            return True
    
    def get_version_info(self, version: str) -> Optional[PolicyVersion]:
        """Get info about a specific policy version"""
        with self._lock:
            return self._versions.get(version)
    
    def _load_policies(self):
        """Load policy versions from file"""
        if not self.policy_file.exists():
            return
        
        try:
            with open(self.policy_file, 'r') as f:
                data = json.load(f)
            
            self._current_version = data.get('current_version', '1.0.0')
            
            versions_data = data.get('versions', {})
            for version, policy_dict in versions_data.items():
                self._versions[version] = PolicyVersion(**policy_dict)
        
        except Exception:
            pass
    
    def _save_policies(self):
        """Save policy versions to file"""
        data = {
            'current_version': self._current_version,
            'versions': {
                version: asdict(policy)
                for version, policy in self._versions.items()
            }
        }
        
        try:
            with open(self.policy_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass


# Global policy manager instance
_policy_manager: Optional[PolicyVersionManager] = None
_policy_lock = threading.Lock()


def get_policy_manager() -> PolicyVersionManager:
    """Get global policy version manager"""
    global _policy_manager
    
    if _policy_manager is None:
        with _policy_lock:
            if _policy_manager is None:
                _policy_manager = PolicyVersionManager()
    
    return _policy_manager


if __name__ == "__main__":
    # Example usage
    manager = get_policy_manager()
    
    print("Current version:", manager.get_current_version())
    
    # Register new version
    manager.register_policy_version(
        "2.0.0",
        "Updated risk assessment logic"
    )
    
    # Canary deployment - 10% traffic
    manager.enable_canary("2.0.0", 10.0)
    
    print("\nCanary test - version distribution:")
    versions = {}
    for i in range(100):
        v = manager.get_policy_version_for_request()
        versions[v] = versions.get(v, 0) + 1
    
    for v, count in versions.items():
        print(f"  {v}: {count}%")
    
    print("\nAll versions:")
    for version, info in manager.list_versions().items():
        print(f"  {version}: {info.description}")
        if info.canary_percentage > 0:
            print(f"    Canary: {info.canary_percentage}%")
