"""
OpenCLI Upgrade Manager
Intelligent upgrade system with step verification and integration testing
"""

import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import sys
import os

class UpgradeManager:
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or Path.home() / ".opencli"
        self.repo_dir = Path.home() / "opencli"
        self.archive_dir = self.repo_dir / "archive"
        self.log_file = self.config_dir / "logs" / "upgrade.log"

        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message, level="INFO"):
        """Log message to file and optionally print"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"

        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")

        return log_entry

    def run_command(self, cmd, cwd=None, timeout=30):
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.repo_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout.strip(),
                'stderr': result.stderr.strip(),
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Command timed out',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }

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

    def get_new_version(self):
        """Get version from repo"""
        version_file = self.repo_dir / "version.json"
        if not version_file.exists():
            return "unknown"

        try:
            with open(version_file) as f:
                data = json.load(f)
                return data.get('version', 'unknown')
        except:
            return "unknown"

    def get_changelog(self, version):
        """Get changelog for specific version"""
        version_file = self.repo_dir / "version.json"
        if not version_file.exists():
            return []

        try:
            with open(version_file) as f:
                data = json.load(f)
                for entry in data.get('changelog', []):
                    if entry.get('version') == version:
                        return entry.get('changes', [])
        except:
            pass

        return []

    def get_verification_steps(self, version):
        """Get verification steps for specific version"""
        version_file = self.repo_dir / "version.json"
        if not version_file.exists():
            return []

        try:
            with open(version_file) as f:
                data = json.load(f)
                for entry in data.get('changelog', []):
                    if entry.get('version') == version:
                        return entry.get('verification_steps', [])
        except:
            pass

        return []

    def get_current_branch(self):
        """Get current git branch"""
        result = self.run_command("git branch --show-current", timeout=5)
        if result['success']:
            return result['stdout'].strip()
        return None

    def preflight_checks(self):
        """Run pre-upgrade checks"""
        checks = []

        # Check if in git repo
        result = self.run_command("git status", timeout=5)
        checks.append({
            'name': 'Git Repository',
            'passed': result['success'],
            'message': 'Git repository detected' if result['success'] else 'Not a git repository'
        })

        if not result['success']:
            return {'passed': False, 'checks': checks}

        # Get current branch
        current_branch = self.get_current_branch()
        if not current_branch:
            checks.append({
                'name': 'Git Branch',
                'passed': False,
                'message': 'Could not determine current branch'
            })
            return {'passed': False, 'checks': checks}

        checks.append({
            'name': 'Current Branch',
            'passed': True,
            'message': f'On branch: {current_branch}',
            'branch': current_branch
        })

        # Check for uncommitted changes
        result = self.run_command("git diff --quiet")
        has_changes = result['returncode'] != 0
        checks.append({
            'name': 'Uncommitted Changes',
            'passed': True,  # Just informational
            'message': 'Local changes detected' if has_changes else 'Working directory clean',
            'warning': has_changes
        })

        # Check if remote updates available (use current branch, not hardcoded main)
        self.run_command("git fetch", timeout=10)
        result = self.run_command(f"git rev-list HEAD...origin/{current_branch} --count")
        updates_available = int(result['stdout'] or '0') > 0
        checks.append({
            'name': 'Remote Updates',
            'passed': True,
            'message': f"{result['stdout'] or '0'} commits available from origin/{current_branch}" if updates_available else f'Up to date with origin/{current_branch}'
        })

        # Check current installation
        checks.append({
            'name': 'Current Installation',
            'passed': self.config_dir.exists(),
            'message': 'Installation directory exists' if self.config_dir.exists() else 'No installation found'
        })

        # Check version files
        checks.append({
            'name': 'Version Metadata',
            'passed': (self.repo_dir / "version.json").exists(),
            'message': 'version.json found' if (self.repo_dir / "version.json").exists() else 'version.json missing'
        })

        # Architecture compliance validation
        arch_check = self.validate_architecture_compliance()
        checks.append({
            'name': 'Architecture Compliance',
            'passed': arch_check['passed'],
            'message': arch_check['message'],
            'details': arch_check.get('details', [])
        })

        all_passed = all(check['passed'] for check in checks)
        return {'passed': all_passed, 'checks': checks}

    def validate_architecture_compliance(self):
        """Validate code follows architecture guidelines"""
        issues = []

        # Check opencli.py line count (max 1200)
        opencli_file = self.repo_dir / "opencli.py"
        if opencli_file.exists():
            line_count = len(opencli_file.read_text().splitlines())
            if line_count > 1200:
                issues.append(f"opencli.py exceeds 1200 lines ({line_count} lines)")
            else:
                issues.append(f"opencli.py: {line_count}/1200 lines ✓")

        # Check module line counts (max 500)
        modules_dir = self.repo_dir / "modules"
        if modules_dir.exists():
            for module_file in modules_dir.glob("*.py"):
                line_count = len(module_file.read_text().splitlines())
                if line_count > 500:
                    issues.append(f"{module_file.name} exceeds 500 lines ({line_count} lines)")

        # Check for required files
        required_files = [
            "opencli.py",
            "version.json",
            "requirements.txt",
            "install.sh",
            "ARCHITECTURE.md"
        ]

        for required_file in required_files:
            if not (self.repo_dir / required_file).exists():
                issues.append(f"Missing required file: {required_file}")

        # Check modules directory
        if not modules_dir.exists():
            issues.append("modules/ directory missing")

        # All checks passed?
        violations = [issue for issue in issues if "exceeds" in issue.lower() or "missing" in issue.lower()]
        passed = len(violations) == 0

        return {
            'passed': passed,
            'message': 'Architecture compliant' if passed else f'{len(violations)} violation(s) found',
            'details': issues
        }

    def compare_branches(self, current_branch):
        """Compare current branch against Main branch"""
        if current_branch == "Main":
            return {
                'comparison': 'none',
                'message': 'Already on Main branch',
                'divergence': None
            }

        # Check if Main branch exists
        result = self.run_command("git show-ref --verify --quiet refs/heads/Main")
        if not result['success']:
            return {
                'comparison': 'error',
                'message': 'Main branch not found',
                'divergence': None
            }

        # Get commits ahead of Main
        result = self.run_command(f"git rev-list Main..{current_branch} --count")
        commits_ahead = int(result['stdout'] or '0')

        # Get commits behind Main
        result = self.run_command(f"git rev-list {current_branch}..Main --count")
        commits_behind = int(result['stdout'] or '0')

        # Get diff summary
        result = self.run_command(f"git diff --stat Main...{current_branch}")
        diff_summary = result['stdout'] if result['success'] else ''

        return {
            'comparison': 'complete',
            'current_branch': current_branch,
            'commits_ahead': commits_ahead,
            'commits_behind': commits_behind,
            'diff_summary': diff_summary,
            'message': f'{commits_ahead} commits ahead, {commits_behind} behind Main'
        }

    def detect_changes(self):
        """Detect what changed between versions"""
        current_branch = self.get_current_branch()

        # Get local uncommitted changes
        result = self.run_command("git diff --stat HEAD")
        local_changes = self._categorize_changes(result['stdout'] if result['success'] else '')

        # Get changes between current branch and Main
        branch_comparison = self.compare_branches(current_branch)

        # Get changes in current branch vs Main
        if current_branch and current_branch != "Main":
            result = self.run_command(f"git diff --stat Main...{current_branch}")
            branch_changes = self._categorize_changes(result['stdout'] if result['success'] else '')
        else:
            branch_changes = {'core': [], 'modules': [], 'agents': [], 'docs': [], 'other': []}

        return {
            'local': local_changes,
            'branch_vs_main': branch_changes,
            'comparison': branch_comparison
        }

    def _categorize_changes(self, diff_output):
        """Helper to categorize changes from git diff output"""
        changes = {
            'core': [],
            'modules': [],
            'agents': [],
            'docs': [],
            'other': []
        }

        if not diff_output:
            return changes

        for line in diff_output.split('\n'):
            if not line.strip():
                continue

            parts = line.split('|')
            if len(parts) < 2:
                continue

            file_path = parts[0].strip()

            # Categorize changes
            if file_path == 'opencli.py' or file_path == 'install.sh':
                changes['core'].append(file_path)
            elif file_path.startswith('modules/'):
                changes['modules'].append(file_path)
            elif file_path.startswith('agents/'):
                changes['agents'].append(file_path)
            elif file_path.endswith('.md'):
                changes['docs'].append(file_path)
            else:
                changes['other'].append(file_path)

        return changes

    def create_backup(self):
        """Create timestamped backup of current installation"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = Path.home() / f".opencli.backup-{timestamp}"

        self.log(f"Creating backup at {backup_dir}")

        try:
            shutil.copytree(self.config_dir, backup_dir, symlinks=True)
            self.log(f"Backup created successfully")
            return {'success': True, 'backup_dir': backup_dir}
        except Exception as e:
            self.log(f"Backup failed: {str(e)}", "ERROR")
            return {'success': False, 'error': str(e)}

    def archive_version(self, version):
        """Archive current version installer"""
        if version == "unknown":
            return {'success': True, 'message': 'Skipped (unknown version)'}

        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Archive install.sh
        archive_name = f"install-v{version}.sh"
        archive_path = self.archive_dir / archive_name

        try:
            install_script = self.repo_dir / "install.sh"
            if install_script.exists():
                shutil.copy2(install_script, archive_path)
                archive_path.chmod(0o755)
                self.log(f"Archived installer: {archive_name}")

            # Archive version.json
            version_file = self.config_dir / "version.json"
            if version_file.exists():
                version_archive = self.archive_dir / f"version-{version}.json"
                shutil.copy2(version_file, version_archive)
                self.log(f"Archived version metadata: version-{version}.json")

            # Update manifest
            self._update_archive_manifest(version)

            return {'success': True, 'archive_path': archive_path}
        except Exception as e:
            self.log(f"Archive failed: {str(e)}", "ERROR")
            return {'success': False, 'error': str(e)}

    def _update_archive_manifest(self, version):
        """Update archive/VERSIONS.md manifest"""
        manifest_path = self.archive_dir / "VERSIONS.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = f"""## v{version} (Archived: {timestamp})
- Install script: install-v{version}.sh
- Version metadata: version-{version}.json
- Archived on: {timestamp}

"""

        # Prepend to existing manifest
        existing_content = ""
        if manifest_path.exists():
            with open(manifest_path) as f:
                lines = f.readlines()
                # Skip header if exists
                if lines and lines[0].startswith('# Archived Versions'):
                    existing_content = ''.join(lines[2:])  # Skip header and blank line
                else:
                    existing_content = ''.join(lines)

        with open(manifest_path, 'w') as f:
            f.write("# Archived Versions\n\n")
            f.write(entry)
            f.write(existing_content)

    def install_new_version(self):
        """Run installation script"""
        self.log("Running installation script")

        install_script = self.repo_dir / "install.sh"
        if not install_script.exists():
            return {'success': False, 'error': 'install.sh not found'}

        result = self.run_command(f"bash {install_script}", timeout=120)

        if result['success']:
            self.log("Installation completed successfully")
        else:
            self.log(f"Installation failed: {result['stderr']}", "ERROR")

        return result

    def verify_installation(self):
        """Run verification tests"""
        tests = []

        # 1. File Integrity
        tests.append(self._verify_file_integrity())

        # 2. Module Imports
        tests.append(self._verify_module_imports())

        # 3. Version Metadata
        tests.append(self._verify_version_metadata())

        # 4. Agent System
        tests.append(self._verify_agent_system())

        # 5. Context System
        tests.append(self._verify_context_system())

        all_passed = all(test['passed'] for test in tests)
        return {'passed': all_passed, 'tests': tests}

    def _verify_file_integrity(self):
        """Verify required files exist"""
        required_files = [
            self.config_dir / "modules" / "agent_manager.py",
            self.config_dir / "modules" / "context_builder.py",
            self.config_dir / "agents" / "configs" / "agents.yaml",
            self.config_dir / "version.json",
            Path.home() / "bin" / "opencli"
        ]

        missing = []
        for file_path in required_files:
            if not file_path.exists():
                missing.append(str(file_path))

        return {
            'name': 'File Integrity',
            'passed': len(missing) == 0,
            'message': 'All required files present' if not missing else f"Missing: {', '.join(missing)}"
        }

    def _verify_module_imports(self):
        """Test module imports"""
        # Add modules directory to path
        modules_dir = self.config_dir / "modules"
        if str(modules_dir) not in sys.path:
            sys.path.insert(0, str(modules_dir))

        modules_to_test = [
            'agent_manager',
            'context_builder',
            'github_tool',
            'upgrade_manager'
        ]

        failed = []
        for module in modules_to_test:
            try:
                __import__(module)
            except ImportError as e:
                failed.append(f"{module} ({str(e)})")

        return {
            'name': 'Module Imports',
            'passed': len(failed) == 0,
            'message': 'All modules import successfully' if not failed else f"Failed: {', '.join(failed)}"
        }

    def _verify_version_metadata(self):
        """Verify version.json structure"""
        version_file = self.config_dir / "version.json"

        if not version_file.exists():
            return {
                'name': 'Version Metadata',
                'passed': False,
                'message': 'version.json not found'
            }

        try:
            with open(version_file) as f:
                data = json.load(f)

            required_fields = ['version', 'release_date', 'changelog']
            missing = [field for field in required_fields if field not in data]

            return {
                'name': 'Version Metadata',
                'passed': len(missing) == 0,
                'message': 'Valid version metadata' if not missing else f"Missing fields: {', '.join(missing)}"
            }
        except Exception as e:
            return {
                'name': 'Version Metadata',
                'passed': False,
                'message': f"Invalid JSON: {str(e)}"
            }

    def _verify_agent_system(self):
        """Verify agent system is functional"""
        agents_config = self.config_dir / "agents" / "configs" / "agents.yaml"

        if not agents_config.exists():
            return {
                'name': 'Agent System',
                'passed': False,
                'message': 'agents.yaml not found'
            }

        try:
            import yaml
            with open(agents_config) as f:
                agents = yaml.safe_load(f)

            if not isinstance(agents, dict) or 'agents' not in agents:
                return {
                    'name': 'Agent System',
                    'passed': False,
                    'message': 'Invalid agents.yaml structure'
                }

            agent_count = len(agents.get('agents', []))
            return {
                'name': 'Agent System',
                'passed': agent_count > 0,
                'message': f"{agent_count} agents configured"
            }
        except Exception as e:
            return {
                'name': 'Agent System',
                'passed': False,
                'message': f"Error: {str(e)}"
            }

    def _verify_context_system(self):
        """Verify context system directories exist"""
        required_dirs = [
            self.config_dir / "agents" / "contexts",
            self.config_dir / "agents" / "temp"
        ]

        missing = []
        for dir_path in required_dirs:
            if not dir_path.exists():
                missing.append(str(dir_path))

        return {
            'name': 'Context System',
            'passed': len(missing) == 0,
            'message': 'Context directories exist' if not missing else f"Missing: {', '.join(missing)}"
        }

    def perform_upgrade(self, auto_rollback=True):
        """
        Perform full upgrade with verification
        Returns: dict with success status and details
        """
        upgrade_log = {
            'started': datetime.now().isoformat(),
            'steps': []
        }

        # Step 1: Pre-flight checks
        self.log("=== UPGRADE STARTED ===")
        self.log("Step 1: Pre-flight checks")

        preflight = self.preflight_checks()
        upgrade_log['steps'].append({
            'name': 'Pre-flight Checks',
            'result': preflight
        })

        if not preflight['passed']:
            self.log("Pre-flight checks failed", "ERROR")
            return {
                'success': False,
                'stage': 'preflight',
                'log': upgrade_log
            }

        # Step 2: Get versions
        current_version = self.get_current_version()
        new_version = self.get_new_version()

        self.log(f"Upgrading from v{current_version} to v{new_version}")
        upgrade_log['current_version'] = current_version
        upgrade_log['new_version'] = new_version

        # Step 3: Detect changes
        self.log("Step 2: Detecting changes")
        changes = self.detect_changes()
        upgrade_log['steps'].append({
            'name': 'Change Detection',
            'result': changes
        })

        # Step 4: Create backup
        self.log("Step 3: Creating backup")
        backup_result = self.create_backup()
        upgrade_log['steps'].append({
            'name': 'Backup Creation',
            'result': backup_result
        })

        if not backup_result['success']:
            self.log("Backup failed - aborting upgrade", "ERROR")
            return {
                'success': False,
                'stage': 'backup',
                'log': upgrade_log
            }

        backup_dir = backup_result['backup_dir']

        # Step 5: Archive old version
        self.log("Step 4: Archiving current version")
        archive_result = self.archive_version(current_version)
        upgrade_log['steps'].append({
            'name': 'Version Archiving',
            'result': archive_result
        })

        # Step 6: Install new version
        self.log("Step 5: Installing new version")
        install_result = self.install_new_version()
        upgrade_log['steps'].append({
            'name': 'Installation',
            'result': install_result
        })

        if not install_result['success']:
            self.log("Installation failed", "ERROR")
            if auto_rollback:
                self.log("Initiating automatic rollback")
                rollback_result = self._perform_rollback(backup_dir)
                upgrade_log['rollback'] = rollback_result

            return {
                'success': False,
                'stage': 'installation',
                'log': upgrade_log,
                'rollback_performed': auto_rollback
            }

        # Step 7: Verify installation
        self.log("Step 6: Verifying installation")
        verification = self.verify_installation()
        upgrade_log['steps'].append({
            'name': 'Verification',
            'result': verification
        })

        if not verification['passed']:
            self.log("Verification failed", "ERROR")
            if auto_rollback:
                self.log("Initiating automatic rollback")
                rollback_result = self._perform_rollback(backup_dir)
                upgrade_log['rollback'] = rollback_result

            return {
                'success': False,
                'stage': 'verification',
                'log': upgrade_log,
                'rollback_performed': auto_rollback
            }

        # Success!
        self.log("=== UPGRADE COMPLETED SUCCESSFULLY ===")
        upgrade_log['completed'] = datetime.now().isoformat()

        return {
            'success': True,
            'current_version': current_version,
            'new_version': new_version,
            'backup_dir': backup_dir,
            'changelog': self.get_changelog(new_version),
            'verification_steps': self.get_verification_steps(new_version),
            'log': upgrade_log
        }

    def _perform_rollback(self, backup_dir):
        """Internal rollback to specific backup"""
        self.log(f"Rolling back to {backup_dir}")

        try:
            # Remove current installation
            if self.config_dir.exists():
                shutil.rmtree(self.config_dir)

            # Restore from backup
            shutil.copytree(backup_dir, self.config_dir, symlinks=True)

            self.log("Rollback completed successfully")
            return {'success': True}
        except Exception as e:
            self.log(f"Rollback failed: {str(e)}", "ERROR")
            return {'success': False, 'error': str(e)}
