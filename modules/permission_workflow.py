"""
Permission Workflow System

Manages multi-step operations that require permission at each step.
Shows status updates in the permission buffer instead of hiding it.
"""

from dataclasses import dataclass
from typing import List, Dict, Callable, Optional, Any
from enum import Enum


class WorkflowStepStatus(Enum):
    """Status of a workflow step"""
    PENDING = "pending"
    WAITING_PERMISSION = "waiting_permission"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """A single step in a permission workflow"""
    id: str
    title: str
    description: str
    requires_permission: bool
    permission_prompt: Optional[Dict] = None  # Prompt data for permission buffer
    execute_func: Optional[Callable] = None  # Async function to execute
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    result: Any = None
    error: Optional[str] = None


class PermissionWorkflow:
    """Manages a multi-step workflow with permission gates"""

    def __init__(self, workflow_id: str, title: str, steps: List[WorkflowStep]):
        self.workflow_id = workflow_id
        self.title = title
        self.steps = steps
        self.current_step_index = 0
        self.completed = False
        self.cancelled = False

    def get_current_step(self) -> Optional[WorkflowStep]:
        """Get the current step"""
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def get_status_summary(self) -> Dict:
        """Get summary of workflow status"""
        completed_count = sum(1 for s in self.steps if s.status == WorkflowStepStatus.COMPLETED)
        failed_count = sum(1 for s in self.steps if s.status == WorkflowStepStatus.FAILED)

        return {
            'workflow_id': self.workflow_id,
            'title': self.title,
            'total_steps': len(self.steps),
            'completed': completed_count,
            'failed': failed_count,
            'current_step': self.current_step_index + 1,
            'current_step_title': self.get_current_step().title if self.get_current_step() else None,
            'is_complete': self.completed,
            'is_cancelled': self.cancelled
        }

    def get_permission_prompt_for_current_step(self) -> Optional[Dict]:
        """Get permission prompt data for current step"""
        step = self.get_current_step()
        if not step or not step.requires_permission:
            return None

        if step.permission_prompt:
            return step.permission_prompt

        # Default permission prompt
        return {
            'title': f'Continue with {step.title}?',
            'message': step.description,
            'options': [
                {
                    'text': 'Yes, continue',
                    'response': 'allow_once',
                    'data': {'workflow_id': self.workflow_id, 'step_id': step.id}
                },
                {
                    'text': 'No, cancel workflow',
                    'response': 'cancel',
                    'data': {'workflow_id': self.workflow_id}
                }
            ]
        }

    async def approve_current_step(self):
        """Mark current step as approved"""
        step = self.get_current_step()
        if step:
            step.status = WorkflowStepStatus.APPROVED

    async def execute_current_step(self) -> bool:
        """Execute the current step"""
        step = self.get_current_step()
        if not step:
            return False

        if step.requires_permission and step.status != WorkflowStepStatus.APPROVED:
            step.status = WorkflowStepStatus.WAITING_PERMISSION
            return False  # Can't execute without approval

        try:
            step.status = WorkflowStepStatus.IN_PROGRESS

            if step.execute_func:
                step.result = await step.execute_func()

            step.status = WorkflowStepStatus.COMPLETED
            return True

        except Exception as e:
            step.status = WorkflowStepStatus.FAILED
            step.error = str(e)
            return False

    async def next_step(self) -> bool:
        """Move to next step"""
        self.current_step_index += 1

        if self.current_step_index >= len(self.steps):
            self.completed = True
            return False

        return True

    def cancel(self):
        """Cancel the workflow"""
        self.cancelled = True
        step = self.get_current_step()
        if step:
            step.status = WorkflowStepStatus.SKIPPED


class WorkflowManager:
    """Manages active permission workflows"""

    def __init__(self):
        self.workflows: Dict[str, PermissionWorkflow] = {}

    def create_workflow(self, workflow_id: str, title: str, steps: List[WorkflowStep]) -> PermissionWorkflow:
        """Create and register a new workflow"""
        workflow = PermissionWorkflow(workflow_id, title, steps)
        self.workflows[workflow_id] = workflow
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[PermissionWorkflow]:
        """Get a workflow by ID"""
        return self.workflows.get(workflow_id)

    def remove_workflow(self, workflow_id: str):
        """Remove a completed workflow"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]

    def get_active_workflows(self) -> List[PermissionWorkflow]:
        """Get all active workflows"""
        return [w for w in self.workflows.values() if not w.completed and not w.cancelled]
