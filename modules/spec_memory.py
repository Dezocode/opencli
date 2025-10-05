"""
Spec Memory - Persistent goal and specification storage
Based on GitHub Spec-Kit principles for long-running agentic workflows
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class SpecMemory:
    """Persistent storage for project specifications and goals"""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize spec memory for a project

        Args:
            project_root: Project root directory (defaults to cwd)
        """
        self.project_root = project_root or Path.cwd()
        self.memory_dir = self.project_root / '.specify' / 'memory'
        self.goals_dir = self.project_root / '.specify' / 'goals'
        self.plans_dir = self.project_root / '.specify' / 'plans'

        # Create directory structure
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.goals_dir.mkdir(parents=True, exist_ok=True)
        self.plans_dir.mkdir(parents=True, exist_ok=True)

    def save_constitution(self, content: str) -> Path:
        """
        Save project constitution (principles and governance)

        Args:
            content: Constitution markdown content

        Returns:
            Path to saved constitution
        """
        path = self.memory_dir / 'constitution.md'
        path.write_text(content)

        # Update metadata
        self._update_metadata('constitution', {
            'updated_at': datetime.now().isoformat(),
            'path': str(path)
        })

        return path

    def load_constitution(self) -> Optional[str]:
        """Load project constitution if it exists"""
        path = self.memory_dir / 'constitution.md'
        if path.exists():
            return path.read_text()
        return None

    def save_feature_spec(self, feature_name: str, spec: str) -> Path:
        """
        Save feature specification

        Args:
            feature_name: Name/ID of feature
            spec: Feature specification markdown

        Returns:
            Path to saved spec
        """
        safe_name = feature_name.replace(' ', '_').lower()
        path = self.memory_dir / f'{safe_name}.spec.md'
        path.write_text(spec)

        self._update_metadata('features', {
            safe_name: {
                'name': feature_name,
                'created_at': datetime.now().isoformat(),
                'path': str(path)
            }
        })

        return path

    def save_plan(self, plan_name: str, plan: Dict) -> Path:
        """
        Save implementation plan

        Args:
            plan_name: Name of plan
            plan: Plan structure with phases and tasks

        Returns:
            Path to saved plan
        """
        safe_name = plan_name.replace(' ', '_').lower()
        path = self.plans_dir / f'{safe_name}.json'

        with open(path, 'w') as f:
            json.dump({
                'name': plan_name,
                'created_at': datetime.now().isoformat(),
                'phases': plan.get('phases', []),
                'tasks': plan.get('tasks', []),
                'current_phase': plan.get('current_phase', 0)
            }, f, indent=2)

        return path

    def load_plan(self, plan_name: str) -> Optional[Dict]:
        """Load implementation plan"""
        safe_name = plan_name.replace(' ', '_').lower()
        path = self.plans_dir / f'{safe_name}.json'

        if path.exists():
            with open(path) as f:
                return json.load(f)
        return None

    def save_goal(self, goal_id: str, goal_data: Dict) -> Path:
        """
        Save current goal state

        Args:
            goal_id: Unique goal identifier
            goal_data: Goal state including description, phase, progress

        Returns:
            Path to saved goal
        """
        path = self.goals_dir / f'{goal_id}.json'

        goal_data['updated_at'] = datetime.now().isoformat()

        with open(path, 'w') as f:
            json.dump(goal_data, f, indent=2)

        return path

    def load_goal(self, goal_id: str) -> Optional[Dict]:
        """Load goal state"""
        path = self.goals_dir / f'{goal_id}.json'

        if path.exists():
            with open(path) as f:
                return json.load(f)
        return None

    def get_active_goals(self) -> List[Dict]:
        """Get all active goals"""
        active_goals = []

        for goal_file in self.goals_dir.glob('*.json'):
            with open(goal_file) as f:
                goal_data = json.load(f)
                if goal_data.get('status') != 'completed':
                    active_goals.append(goal_data)

        return sorted(active_goals, key=lambda g: g.get('updated_at', ''), reverse=True)

    def get_active_context(self) -> Dict:
        """
        Load all active specifications into context

        Returns:
            Dictionary with constitution, features, plans, and goals
        """
        context = {}

        # Load constitution
        constitution = self.load_constitution()
        if constitution:
            context['constitution'] = constitution

        # Load feature specs
        context['features'] = {}
        for spec_file in self.memory_dir.glob('*.spec.md'):
            feature_name = spec_file.stem.replace('.spec', '')
            context['features'][feature_name] = spec_file.read_text()

        # Load active plans
        context['plans'] = []
        for plan_file in self.plans_dir.glob('*.json'):
            with open(plan_file) as f:
                plan = json.load(f)
                if plan.get('current_phase', 0) < len(plan.get('phases', [])):
                    context['plans'].append(plan)

        # Load active goals
        context['goals'] = self.get_active_goals()

        return context

    def _update_metadata(self, category: str, data: Dict):
        """Update metadata index"""
        metadata_path = self.memory_dir / 'metadata.json'

        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)
        else:
            metadata = {}

        if category not in metadata:
            metadata[category] = {}

        if isinstance(data, dict):
            metadata[category].update(data)
        else:
            metadata[category] = data

        metadata['last_updated'] = datetime.now().isoformat()

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def get_metadata(self) -> Dict:
        """Get all metadata"""
        metadata_path = self.memory_dir / 'metadata.json'

        if metadata_path.exists():
            with open(metadata_path) as f:
                return json.load(f)
        return {}

    def clear_completed_goals(self):
        """Archive completed goals"""
        archive_dir = self.goals_dir / 'archive'
        archive_dir.mkdir(exist_ok=True)

        for goal_file in self.goals_dir.glob('*.json'):
            with open(goal_file) as f:
                goal_data = json.load(f)

            if goal_data.get('status') == 'completed':
                # Move to archive
                archive_path = archive_dir / goal_file.name
                goal_file.rename(archive_path)

    def format_context_for_system_message(self) -> str:
        """
        Format active context for system message

        Returns:
            Formatted markdown string for system context
        """
        context = self.get_active_context()
        parts = []

        # Constitution
        if context.get('constitution'):
            parts.append("# Project Constitution\n")
            parts.append(context['constitution'])
            parts.append("\n---\n")

        # Active Goals
        if context.get('goals'):
            parts.append("# Active Goals\n")
            for goal in context['goals']:
                parts.append(f"\n## {goal.get('description', 'Unnamed Goal')}\n")
                parts.append(f"- **Phase**: {goal.get('phase', 'planning')}\n")
                parts.append(f"- **Status**: {goal.get('status', 'active')}\n")
                if goal.get('progress'):
                    parts.append(f"- **Progress**: {len(goal['progress'])} actions completed\n")
            parts.append("\n---\n")

        # Active Plans
        if context.get('plans'):
            parts.append("# Active Plans\n")
            for plan in context['plans']:
                parts.append(f"\n## {plan.get('name', 'Unnamed Plan')}\n")
                current_phase = plan.get('current_phase', 0)
                phases = plan.get('phases', [])
                if current_phase < len(phases):
                    parts.append(f"- **Current Phase**: {phases[current_phase]}\n")
            parts.append("\n---\n")

        return ''.join(parts)
