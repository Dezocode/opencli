"""
Authorization Facade - Single Entry Point for All Authorization Decisions

This is the ONLY place where authorization decisions are made.
All other parts of the system MUST call this facade.

Design Principles:
1. Single Responsibility: Only makes authorization decisions
2. Acyclic Dependencies: Never imports domain models or business logic
3. Policy as Data: Policies loaded from external source, not hardcoded
4. Auditable: Every decision is logged with full context
5. Testable: Clean interface with no hidden dependencies

Decision Flow:
    check_authorization() 
    → assess_risk()
    → evaluate_policy()
    → log_decision()
    → return AuthzDecision
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List
import threading

# Configure structured logging for authorization decisions
logger = logging.getLogger("opencli.authz")


class AuthzAction(str, Enum):
    """Standard actions for authorization"""
    # File operations
    FILE_READ = "file:read"
    FILE_WRITE = "file:write"
    FILE_EDIT = "file:edit"
    FILE_DELETE = "file:delete"
    
    # Bash operations
    BASH_EXECUTE = "bash:execute"
    
    # API operations
    API_CALL = "api:call"
    
    # Tool operations
    TOOL_EXECUTE = "tool:execute"
    
    # Command operations
    COMMAND_EXECUTE = "command:execute"


class RiskLevel(str, Enum):
    """Risk levels for operations"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionResult(str, Enum):
    """Authorization decision results"""
    ALLOW = "allow"
    DENY = "deny"
    PROMPT = "prompt"


@dataclass
class AuthzSubject:
    """Subject requesting authorization (user, service, etc.)"""
    id: str
    type: str = "user"
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthzContext:
    """Context for authorization decision"""
    # Core context
    subject: AuthzSubject
    action: str
    resource: str
    
    # Additional context
    risk_level: Optional[RiskLevel] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # For audit trail
    request_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class AuthzDecision:
    """Result of authorization decision"""
    allowed: bool
    result: DecisionResult
    reason: str
    risk_level: RiskLevel
    context: AuthzContext
    decision_time: float = field(default_factory=time.time)
    policy_version: Optional[str] = None
    decision_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "allowed": self.allowed,
            "result": self.result.value,
            "reason": self.reason,
            "risk_level": self.risk_level.value,
            "subject": self.context.subject.id,
            "action": self.context.action,
            "resource": self.context.resource,
            "decision_time": self.decision_time,
            "policy_version": self.policy_version,
            "decision_path": self.decision_path,
            "request_id": self.context.request_id
        }


class AuthorizationManager:
    """
    Central authorization manager - singleton instance
    
    This is the canonical source of truth for authorization decisions.
    PHASE 3: Now includes policy versioning
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._decision_log: List[AuthzDecision] = []
        
        # PHASE 3: Policy versioning support
        try:
            from .policy_versioning import get_policy_manager
            self._policy_manager = get_policy_manager()
            self._policy_version = self._policy_manager.get_current_version()
        except ImportError:
            self._policy_manager = None
            self._policy_version = "1.0.0"
        
        # Legacy compatibility: reference to existing permission managers
        self._legacy_permission_manager = None
        self._legacy_risk_manager = None
        
        logger.info("AuthorizationManager initialized", extra={
            "policy_version": self._policy_version,
            "instance_id": id(self),
            "policy_versioning_enabled": self._policy_manager is not None
        })
    
    def set_legacy_managers(self, permission_manager, risk_manager):
        """
        Set legacy managers for backward compatibility during migration.
        This allows the facade to delegate to existing implementations
        while we gradually migrate all code paths.
        """
        with self._lock:
            self._legacy_permission_manager = permission_manager
            self._legacy_risk_manager = risk_manager
            logger.info("Legacy managers registered for backward compatibility")
    
    async def check_authorization(
        self,
        subject: AuthzSubject,
        action: str,
        resource: str,
        context: Optional[Dict[str, Any]] = None,
        app=None,
        session=None
    ) -> AuthzDecision:
        """
        THE CANONICAL AUTHORIZATION CHECK
        
        This is the single entry point for ALL authorization decisions.
        PHASE 3: Now includes performance monitoring
        
        Args:
            subject: Who is requesting access
            action: What they want to do (use AuthzAction enum)
            resource: What they want to access
            context: Additional context for the decision
            app: TUI app for showing prompts (optional)
            session: Session object (optional)
        
        Returns:
            AuthzDecision with full audit trail
        """
        # PHASE 3: Start performance timer
        start_time = time.time()
        
        ctx = AuthzContext(
            subject=subject,
            action=action,
            resource=resource,
            metadata=context or {},
            request_id=f"authz_{time.time()}"
        )
        
        logger.info(
            f"Authorization check: {subject.id} -> {action} on {resource}",
            extra=ctx.__dict__
        )
        
        # Phase 1: Assess risk
        risk_level = await self._assess_risk(ctx)
        ctx.risk_level = risk_level
        
        # Phase 2: Check if we need to prompt user
        decision_result = await self._evaluate_policy(ctx, app, session)
        
        # PHASE 3: Get policy version for this request (considers canary)
        policy_version = self._policy_version
        if self._policy_manager:
            policy_version = self._policy_manager.get_policy_version_for_request()
        
        # Phase 3: Create decision
        decision = AuthzDecision(
            allowed=(decision_result == DecisionResult.ALLOW),
            result=decision_result,
            reason=self._get_decision_reason(decision_result, risk_level),
            risk_level=risk_level,
            context=ctx,
            policy_version=policy_version,
            decision_path="authz.facade.check_authorization"
        )
        
        # Phase 4: Log the decision
        self._log_decision(decision)
        
        # PHASE 3: Record performance metrics
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        try:
            from .performance import record_authorization_decision
            record_authorization_decision(
                latency_ms=latency_ms,
                decision_result=decision_result.value,
                risk_level=risk_level.value,
                cache_hit=False  # TODO: Implement caching in future
            )
        except ImportError:
            pass  # Performance monitoring not available
        
        return decision
    
    async def _assess_risk(self, context: AuthzContext) -> RiskLevel:
        """
        Assess risk level for the operation
        
        This consolidates risk assessment from:
        - Path-based risk (file operations)
        - Command-based risk (bash)
        - API-based risk (cost, quota)
        """
        # If legacy risk manager is available, use it during migration
        if self._legacy_risk_manager:
            try:
                from ..permissions.risk_assessment import RiskLevel as LegacyRiskLevel
                
                # Map action to tool_name for legacy compatibility
                tool_name = self._map_action_to_tool(context.action)
                args = context.metadata.get("args", {})
                current_dir = context.metadata.get("current_dir")
                
                legacy_risk, reason = self._legacy_risk_manager.assess_operation_risk(
                    tool_name, args, current_dir
                )
                
                # Map legacy risk level to our enum
                risk_map = {
                    "safe": RiskLevel.SAFE,
                    "low": RiskLevel.LOW,
                    "medium": RiskLevel.MEDIUM,
                    "high": RiskLevel.HIGH,
                    "critical": RiskLevel.CRITICAL
                }
                return risk_map.get(legacy_risk.value.lower(), RiskLevel.MEDIUM)
            except Exception as e:
                logger.warning(f"Legacy risk assessment failed: {e}")
        
        # Default risk assessment
        return self._default_risk_assessment(context)
    
    def _default_risk_assessment(self, context: AuthzContext) -> RiskLevel:
        """Default risk assessment when legacy managers not available"""
        action = context.action
        resource = context.resource
        
        # Critical operations
        if action in [AuthzAction.FILE_DELETE, AuthzAction.BASH_EXECUTE]:
            # Check if affecting system paths
            if any(critical in resource.lower() for critical in [
                "/etc", "/bin", "/usr", "/system", "/.ssh", "/.aws"
            ]):
                return RiskLevel.CRITICAL
            return RiskLevel.HIGH
        
        # Medium risk operations
        if action in [AuthzAction.FILE_WRITE, AuthzAction.FILE_EDIT]:
            # Check if outside current directory
            try:
                cwd = Path.cwd().resolve()
                target = Path(resource).resolve()
                target.relative_to(cwd)
                return RiskLevel.MEDIUM
            except ValueError:
                # Outside current directory
                return RiskLevel.HIGH
        
        # Low risk operations
        if action == AuthzAction.FILE_READ:
            return RiskLevel.LOW
        
        return RiskLevel.MEDIUM
    
    async def _evaluate_policy(
        self,
        context: AuthzContext,
        app=None,
        session=None
    ) -> DecisionResult:
        """
        Evaluate policy to determine if operation should be allowed
        
        Policy evaluation order:
        1. Always allow SAFE risk operations
        2. Always prompt for CRITICAL risk operations
        3. Check user preferences and auto-accept modes
        4. Prompt user for decision
        """
        risk = context.risk_level
        
        # Always allow safe operations
        if risk == RiskLevel.SAFE:
            return DecisionResult.ALLOW
        
        # For backward compatibility, delegate to legacy permission manager
        if self._legacy_permission_manager and app and session:
            try:
                # Create registration object for legacy compatibility
                from ..execution.registry import ExecutionRegistration, ExecutionType, RiskLevel as ExecRiskLevel
                
                # Map our risk level to execution risk level
                risk_map = {
                    RiskLevel.SAFE: ExecRiskLevel.SAFE,
                    RiskLevel.LOW: ExecRiskLevel.LOW,
                    RiskLevel.MEDIUM: ExecRiskLevel.MEDIUM,
                    RiskLevel.HIGH: ExecRiskLevel.HIGH,
                    RiskLevel.CRITICAL: ExecRiskLevel.CRITICAL
                }
                
                registration = ExecutionRegistration(
                    type=ExecutionType.COMMAND,
                    name=context.action,
                    handler=None,
                    description=f"Authorization check for {context.action}",
                    requires_approval=True,
                    risk_level=risk_map.get(risk, ExecRiskLevel.MEDIUM)
                )
                
                legacy_context = {
                    **context.metadata,
                    "resource": context.resource
                }
                
                approved = await self._legacy_permission_manager.check_permission(
                    registration, legacy_context, app, session
                )
                
                return DecisionResult.ALLOW if approved else DecisionResult.DENY
                
            except Exception as e:
                logger.warning(f"Legacy policy evaluation failed: {e}")
        
        # Default: prompt for medium and above
        if risk in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return DecisionResult.PROMPT
        
        return DecisionResult.ALLOW
    
    def _map_action_to_tool(self, action: str) -> str:
        """Map our action enum to legacy tool names"""
        mapping = {
            "file:read": "Read",
            "file:write": "Write",
            "file:edit": "Edit",
            "file:delete": "Delete",
            "bash:execute": "Bash",
            "api:call": "API",
            "tool:execute": "Tool",
            "command:execute": "Command"
        }
        return mapping.get(action, "Unknown")
    
    def _get_decision_reason(self, result: DecisionResult, risk: RiskLevel) -> str:
        """Generate human-readable reason for decision"""
        if result == DecisionResult.ALLOW:
            if risk == RiskLevel.SAFE:
                return "Safe operation - auto-approved"
            return "Operation approved"
        elif result == DecisionResult.DENY:
            return "Operation denied by policy"
        else:
            return f"User prompt required for {risk.value} risk operation"
    
    def _log_decision(self, decision: AuthzDecision):
        """Log authorization decision for audit trail"""
        with self._lock:
            self._decision_log.append(decision)
            
            # Keep only last 1000 decisions in memory
            if len(self._decision_log) > 1000:
                self._decision_log = self._decision_log[-1000:]
        
        # Structured logging
        logger.info(
            f"Authorization decision: {decision.result.value}",
            extra=decision.to_dict()
        )
    
    def get_decision_log(
        self,
        subject_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[AuthzDecision]:
        """Get recent authorization decisions for audit"""
        with self._lock:
            decisions = self._decision_log[-limit:]
            
            if subject_id:
                decisions = [d for d in decisions if d.context.subject.id == subject_id]
            
            if action:
                decisions = [d for d in decisions if d.context.action == action]
            
            return decisions
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get authorization metrics"""
        with self._lock:
            total = len(self._decision_log)
            if total == 0:
                return {"total_decisions": 0}
            
            allowed = sum(1 for d in self._decision_log if d.allowed)
            denied = total - allowed
            
            by_risk = {}
            for decision in self._decision_log:
                risk = decision.risk_level.value
                by_risk[risk] = by_risk.get(risk, 0) + 1
            
            return {
                "total_decisions": total,
                "allowed": allowed,
                "denied": denied,
                "allow_rate": allowed / total if total > 0 else 0,
                "by_risk_level": by_risk
            }


# Global singleton instance
_authz_manager: Optional[AuthorizationManager] = None
_authz_lock = threading.Lock()


def get_authz_manager() -> AuthorizationManager:
    """Get the global authorization manager instance"""
    global _authz_manager
    
    if _authz_manager is None:
        with _authz_lock:
            if _authz_manager is None:
                _authz_manager = AuthorizationManager()
    
    return _authz_manager


async def check_authorization(
    subject: AuthzSubject,
    action: str,
    resource: str,
    context: Optional[Dict[str, Any]] = None,
    app=None,
    session=None
) -> AuthzDecision:
    """
    THE CANONICAL AUTHORIZATION CHECK - Single Entry Point
    
    This function MUST be used for ALL authorization decisions.
    Do not import or call any other permission/authorization functions.
    
    Example:
        from modules.authz import check_authorization, AuthzSubject
        
        subject = AuthzSubject(id=session.id, type="user")
        decision = await check_authorization(
            subject=subject,
            action="file:write",
            resource="/path/to/file",
            context={"args": {...}}
        )
        
        if decision.allowed:
            # Proceed with operation
            pass
        else:
            # Deny operation
            pass
    """
    manager = get_authz_manager()
    return await manager.check_authorization(
        subject=subject,
        action=action,
        resource=resource,
        context=context,
        app=app,
        session=session
    )
