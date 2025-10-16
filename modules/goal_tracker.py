"""
Goal Tracker - Track agent goals with sanity validation
Ensures tool calls align with stated goals and track forward progress
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class GoalSanityError(Exception):
    """Raised when tool call doesn't align with current goal"""
    pass


class GoalTracker:
    """Track agent goals across long-running sessions with sanity validation"""

    PHASES = ['planning', 'implementing', 'testing', 'refining', 'complete']

    def __init__(self, session_id: str, spec_memory=None, verbose=False):
        """
        Initialize goal tracker

        Args:
            session_id: Current session ID
            spec_memory: SpecMemory instance for persistence
            verbose: Enable verbose logging
        """
        self.session_id = session_id
        self.spec_memory = spec_memory
        self.verbose = verbose

        # Current active goal
        self.current_goal: Optional[Dict] = None

        # Goal history for this session
        self.goal_history: List[Dict] = []

        # Tool execution tracking
        self.tool_executions: List[Dict] = []

        # Checkpoints for recovery
        self.checkpoints: List[Dict] = []

        # Load active goals from spec memory if available
        if self.spec_memory:
            active_goals = self.spec_memory.get_active_goals()
            if active_goals:
                # Resume most recent active goal
                self.current_goal = active_goals[0]
                self.goal_history = [self.current_goal]

    def set_goal(self, description: str, phase: str = 'planning', context: Optional[Dict] = None) -> str:
        """
        Set new goal and persist it

        Args:
            description: Clear description of goal
            phase: Current phase (planning, implementing, testing, refining, complete)
            context: Additional context (feature spec, plan reference, etc.)

        Returns:
            Goal ID
        """
        goal_id = str(uuid.uuid4())[:8]

        self.current_goal = {
            'id': goal_id,
            'description': description,
            'phase': phase,
            'status': 'active',
            'started_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'progress': [],
            'tool_calls': 0,
            'context': context or {},
            'session_id': self.session_id
        }

        self.goal_history.append(self.current_goal)

        # Persist to spec memory
        if self.spec_memory:
            self.spec_memory.save_goal(goal_id, self.current_goal)

        if self.verbose:
            print(f"🎯 Goal set: {description} (phase: {phase})")

        return goal_id

    def update_phase(self, new_phase: str):
        """Move to next phase of goal"""
        if not self.current_goal:
            raise ValueError("No active goal to update")

        if new_phase not in self.PHASES:
            raise ValueError(f"Invalid phase: {new_phase}")

        old_phase = self.current_goal['phase']
        self.current_goal['phase'] = new_phase
        self.current_goal['updated_at'] = datetime.now().isoformat()

        # Record phase transition
        self.add_progress(
            action=f"phase_transition:{old_phase}→{new_phase}",
            result="Phase updated",
            metadata={'old_phase': old_phase, 'new_phase': new_phase}
        )

        if self.verbose:
            print(f"📊 Phase transition: {old_phase} → {new_phase}")

        # Persist update
        if self.spec_memory and self.current_goal:
            self.spec_memory.save_goal(self.current_goal['id'], self.current_goal)

    def add_progress(self, action: str, result: str, metadata: Optional[Dict] = None):
        """
        Record progress on current goal

        Args:
            action: Action taken (tool call, decision, etc.)
            result: Result of action
            metadata: Additional metadata
        """
        if not self.current_goal:
            if self.verbose:
                print("⚠️ No active goal - progress not tracked")
            return

        progress_entry = {
            'action': action,
            'result': result,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        self.current_goal['progress'].append(progress_entry)
        self.current_goal['updated_at'] = datetime.now().isoformat()

        # Persist update
        if self.spec_memory:
            self.spec_memory.save_goal(self.current_goal['id'], self.current_goal)

    def validate_tool_call(self, tool_name: str, args: Dict) -> Tuple[bool, str]:
        """
        Validate if tool call aligns with current goal (SANITY CHECK)

        Args:
            tool_name: Name of tool being called
            args: Tool arguments

        Returns:
            (is_valid, reason) - True if aligned with goal, False otherwise
        """
        if not self.current_goal:
            # No goal set - allow but warn
            return (True, "No active goal - allowing tool call")

        goal_desc = self.current_goal['description'].lower()
        phase = self.current_goal['phase']

        # Phase-based validation
        if phase == 'planning':
            # Planning phase: Read, Grep, Glob are expected
            if tool_name in ['Read', 'Grep', 'Glob']:
                return (True, f"Planning phase: {tool_name} appropriate for investigation")
            elif tool_name in ['Write', 'Edit']:
                return (False, f"Planning phase: {tool_name} should not modify code yet")

        elif phase == 'implementing':
            # Implementing phase: Write, Edit, Bash are expected
            if tool_name in ['Write', 'Edit', 'Bash']:
                return (True, f"Implementing phase: {tool_name} appropriate for changes")

        elif phase == 'testing':
            # Testing phase: Bash for running tests
            if tool_name == 'Bash':
                cmd = args.get('command', '')
                if any(keyword in cmd.lower() for keyword in ['test', 'pytest', 'npm test', 'jest']):
                    return (True, "Testing phase: Running tests")
            elif tool_name in ['Read', 'Grep']:
                return (True, "Testing phase: Investigating test results")

        # Context-based validation
        context = self.current_goal.get('context', {})

        # Check if tool args relate to goal context
        if 'files' in context:
            expected_files = context['files']
            # Check if tool is operating on expected files
            file_path = args.get('file_path', args.get('pattern', ''))
            if file_path:
                if any(ef in str(file_path) for ef in expected_files):
                    return (True, f"Tool operating on goal-related file: {file_path}")

        # Default: Allow but note uncertainty
        return (True, f"Tool call permitted - goal: {self.current_goal['description'][:50]}")

    def record_tool_call(self, tool_name: str, args: Dict, result: str, sanity_check: Tuple[bool, str]):
        """
        Record tool call with sanity check result

        Args:
            tool_name: Name of tool
            args: Tool arguments
            result: Tool execution result
            sanity_check: (is_valid, reason) from validate_tool_call
        """
        tool_record = {
            'tool_name': tool_name,
            'args': args,
            'result': result[:200],  # Truncate long results
            'timestamp': datetime.now().isoformat(),
            'sanity_check': {
                'valid': sanity_check[0],
                'reason': sanity_check[1]
            },
            'goal_id': self.current_goal['id'] if self.current_goal else None
        }

        self.tool_executions.append(tool_record)

        # Update current goal stats
        if self.current_goal:
            self.current_goal['tool_calls'] = self.current_goal.get('tool_calls', 0) + 1

            # Add to progress
            self.add_progress(
                action=f"tool:{tool_name}",
                result=result[:100],
                metadata={
                    'tool_name': tool_name,
                    'sanity_valid': sanity_check[0],
                    'sanity_reason': sanity_check[1]
                }
            )

    def create_checkpoint(self, messages: List[Dict]) -> Dict:
        """
        Create recovery checkpoint

        Args:
            messages: Current session messages

        Returns:
            Checkpoint data
        """
        checkpoint = {
            'id': str(uuid.uuid4())[:8],
            'goal': self.current_goal,
            'timestamp': datetime.now().isoformat(),
            'messages_count': len(messages),
            'tool_calls_count': len(self.tool_executions),
            'phase': self.current_goal['phase'] if self.current_goal else None
        }

        self.checkpoints.append(checkpoint)

        if self.verbose:
            print(f"💾 Checkpoint created: {checkpoint['id']}")

        return checkpoint

    def get_goal_summary(self) -> str:
        """
        Get formatted summary of current goal and progress

        Returns:
            Markdown-formatted summary
        """
        if not self.current_goal:
            return "No active goal set."

        lines = [
            f"# Current Goal: {self.current_goal['description']}",
            f"",
            f"**Phase**: {self.current_goal['phase']}",
            f"**Status**: {self.current_goal['status']}",
            f"**Tool Calls**: {self.current_goal.get('tool_calls', 0)}",
            f"**Progress Entries**: {len(self.current_goal.get('progress', []))}",
            f"**Started**: {self.current_goal['started_at']}",
            f""
        ]

        # Show recent progress
        progress = self.current_goal.get('progress', [])
        if progress:
            lines.append("## Recent Progress:")
            for entry in progress[-5:]:  # Last 5 entries
                lines.append(f"- **{entry['action']}**: {entry['result'][:80]}")

        return '\n'.join(lines)

    def get_context_for_system_message(self) -> str:
        """
        Format goal context for system message

        Returns:
            Formatted context string
        """
        if not self.current_goal:
            return ""

        return f"""
# Active Goal Context

**Current Goal**: {self.current_goal['description']}
**Phase**: {self.current_goal['phase']}
**Progress**: {len(self.current_goal.get('progress', []))} actions completed

**Important**: All tool calls should align with this goal. The system validates that your actions move toward completing this goal.
"""

    def complete_goal(self, outcome: str):
        """Mark current goal as complete"""
        if not self.current_goal:
            return

        self.current_goal['status'] = 'completed'
        self.current_goal['completed_at'] = datetime.now().isoformat()
        self.current_goal['outcome'] = outcome
        self.current_goal['phase'] = 'complete'

        # Persist
        if self.spec_memory:
            self.spec_memory.save_goal(self.current_goal['id'], self.current_goal)

        if self.verbose:
            print(f"✅ Goal completed: {self.current_goal['description']}")

        # Clear current goal
        self.current_goal = None

    def get_statistics(self) -> Dict:
        """Get goal tracking statistics"""
        total_goals = len(self.goal_history)
        completed_goals = len([g for g in self.goal_history if g.get('status') == 'completed'])
        total_tools = len(self.tool_executions)
        failed_sanity = len([t for t in self.tool_executions if not t['sanity_check']['valid']])

        return {
            'total_goals': total_goals,
            'completed_goals': completed_goals,
            'active_goals': total_goals - completed_goals,
            'total_tool_calls': total_tools,
            'failed_sanity_checks': failed_sanity,
            'sanity_failure_rate': failed_sanity / total_tools if total_tools > 0 else 0,
            'checkpoints': len(self.checkpoints)
        }
