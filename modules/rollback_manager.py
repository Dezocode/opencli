"""
OpenCLI Rollback Manager
Standalone rollback system that works even if main CLI is broken
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import os

class RollbackManager:
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.backup_pattern = Path.home() / ".opencli.backup-*"

    def list_backups(self):
        """List all available backups with metadata"""
        backup_dirs = sorted(
            Path.home().glob(".opencli.backup-*"),
            key=lambda p: p.name,
            reverse=True
        )

        backups = []
        for backup_dir in backup_dirs:
            # Parse timestamp from directory name
            timestamp_str = backup_dir.name.replace('.opencli.backup-', '')

            try:
                # Format: YYYYMMDD-HHMMSS
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S")
            except:
                timestamp = None

            # Get version from backup
            version_file = backup_dir / "version.json"
            version = "unknown"
            if version_file.exists():
                try:
                    with open(version_file) as f:
                        data = json.load(f)
                        version = data.get('version', 'unknown')
                except:
                    pass

            # Calculate age
            age_str = "unknown age"
            if timestamp:
                age = datetime.now() - timestamp
                if age.days > 0:
                    age_str = f"{age.days} day{'s' if age.days != 1 else ''} ago"
                elif age.seconds // 3600 > 0:
                    hours = age.seconds // 3600
                    age_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
                else:
                    minutes = age.seconds // 60
                    age_str = f"{minutes} minute{'s' if minutes != 1 else ''} ago"

            backups.append({
                'path': backup_dir,
                'version': version,
                'timestamp': timestamp,
                'timestamp_str': timestamp_str,
                'age': age_str,
                'size': self._get_dir_size(backup_dir)
            })

        return backups

    def _get_dir_size(self, path):
        """Get human-readable directory size"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except:
            return "unknown"

        # Convert to human-readable
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total < 1024.0:
                return f"{total:.1f} {unit}"
            total /= 1024.0

        return f"{total:.1f} TB"

    def get_current_version(self):
        """Get currently installed version"""
        version_file = self.config_dir / "version.json"
        if not version_file.exists():
            return "unknown"

        try:
            with open(version_file) as f:
                data = json.load(f)
                return data.get('version', 'unknown')
        except:
            return "unknown"

    def verify_backup(self, backup_path):
        """Verify backup is valid and complete"""
        checks = []

        # Check if directory exists
        if not backup_path.exists():
            return {
                'valid': False,
                'checks': [{'name': 'Directory', 'passed': False, 'message': 'Backup directory not found'}]
            }

        # Check required directories
        required_dirs = ['modules', 'agents', 'sessions']
        for dir_name in required_dirs:
            dir_path = backup_path / dir_name
            checks.append({
                'name': f'{dir_name}/',
                'passed': dir_path.exists(),
                'message': 'exists' if dir_path.exists() else 'missing'
            })

        # Check version.json
        version_file = backup_path / "version.json"
        checks.append({
            'name': 'version.json',
            'passed': version_file.exists(),
            'message': 'exists' if version_file.exists() else 'missing'
        })

        # Check modules
        modules_dir = backup_path / "modules"
        if modules_dir.exists():
            module_count = len(list(modules_dir.glob('*.py')))
            checks.append({
                'name': 'modules/*.py',
                'passed': module_count > 0,
                'message': f'{module_count} modules' if module_count > 0 else 'no modules'
            })

        # Check agents config
        agents_config = backup_path / "agents" / "configs" / "agents.yaml"
        checks.append({
            'name': 'agents.yaml',
            'passed': agents_config.exists(),
            'message': 'exists' if agents_config.exists() else 'missing'
        })

        all_passed = all(check['passed'] for check in checks)
        return {
            'valid': all_passed,
            'checks': checks
        }

    def create_safety_backup(self, suffix="broken"):
        """Create backup of current (potentially broken) state"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safety_backup_dir = Path.home() / f".opencli.{suffix}-{timestamp}"

        try:
            if self.config_dir.exists():
                shutil.copytree(self.config_dir, safety_backup_dir, symlinks=True)
                return {
                    'success': True,
                    'backup_dir': safety_backup_dir
                }
            else:
                return {
                    'success': False,
                    'error': 'No installation to backup'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def perform_rollback(self, backup_path, create_safety=True):
        """
        Perform rollback to specified backup
        Returns: dict with success status and details
        """
        rollback_log = {
            'started': datetime.now().isoformat(),
            'backup_path': str(backup_path),
            'steps': []
        }

        # Step 1: Verify backup
        verification = self.verify_backup(backup_path)
        rollback_log['steps'].append({
            'name': 'Backup Verification',
            'result': verification
        })

        if not verification['valid']:
            return {
                'success': False,
                'stage': 'verification',
                'log': rollback_log
            }

        # Step 2: Create safety backup
        if create_safety:
            safety_result = self.create_safety_backup()
            rollback_log['steps'].append({
                'name': 'Safety Backup',
                'result': safety_result
            })

            if not safety_result['success']:
                rollback_log['warning'] = 'Could not create safety backup, but continuing...'

        # Step 3: Get versions
        current_version = self.get_current_version()
        backup_version_file = backup_path / "version.json"
        backup_version = "unknown"

        if backup_version_file.exists():
            try:
                with open(backup_version_file) as f:
                    data = json.load(f)
                    backup_version = data.get('version', 'unknown')
            except:
                pass

        rollback_log['current_version'] = current_version
        rollback_log['backup_version'] = backup_version

        # Step 4: Remove current installation
        try:
            if self.config_dir.exists():
                shutil.rmtree(self.config_dir)

            rollback_log['steps'].append({
                'name': 'Remove Current Installation',
                'result': {'success': True}
            })
        except Exception as e:
            rollback_log['steps'].append({
                'name': 'Remove Current Installation',
                'result': {'success': False, 'error': str(e)}
            })

            return {
                'success': False,
                'stage': 'removal',
                'log': rollback_log
            }

        # Step 5: Restore from backup
        try:
            shutil.copytree(backup_path, self.config_dir, symlinks=True)

            rollback_log['steps'].append({
                'name': 'Restore from Backup',
                'result': {'success': True}
            })
        except Exception as e:
            rollback_log['steps'].append({
                'name': 'Restore from Backup',
                'result': {'success': False, 'error': str(e)}
            })

            return {
                'success': False,
                'stage': 'restoration',
                'log': rollback_log
            }

        # Step 6: Verify restored installation
        verify_result = self._verify_restoration()
        rollback_log['steps'].append({
            'name': 'Verify Restoration',
            'result': verify_result
        })

        # Success!
        rollback_log['completed'] = datetime.now().isoformat()

        return {
            'success': True,
            'current_version': current_version,
            'backup_version': backup_version,
            'backup_path': backup_path,
            'safety_backup': safety_result.get('backup_dir') if create_safety else None,
            'log': rollback_log
        }

    def _verify_restoration(self):
        """Verify restored installation basic structure"""
        checks = []

        required_paths = [
            self.config_dir / "modules",
            self.config_dir / "agents",
            self.config_dir / "version.json"
        ]

        for path in required_paths:
            checks.append({
                'name': str(path.relative_to(self.config_dir)),
                'passed': path.exists(),
                'message': 'exists' if path.exists() else 'missing'
            })

        all_passed = all(check['passed'] for check in checks)
        return {
            'success': all_passed,
            'checks': checks
        }

    def cleanup_old_backups(self, keep_latest=5):
        """Remove old backups, keeping only the most recent"""
        backups = self.list_backups()

        if len(backups) <= keep_latest:
            return {
                'success': True,
                'removed': 0,
                'message': f'Keeping all {len(backups)} backups'
            }

        backups_to_remove = backups[keep_latest:]
        removed_count = 0

        for backup in backups_to_remove:
            try:
                shutil.rmtree(backup['path'])
                removed_count += 1
            except Exception as e:
                pass  # Continue with others

        return {
            'success': True,
            'removed': removed_count,
            'kept': keep_latest,
            'message': f'Removed {removed_count} old backups'
        }
