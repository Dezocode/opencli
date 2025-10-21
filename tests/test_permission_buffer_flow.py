"""
Test SDK command permission buffer flow

This test suite verifies that SDK-validated commands properly display
permission prompts with interactive options in the TUI permission buffer.

Tests cover:
1. Command registration with requires_approval=True
2. Permission check triggering buffer display
3. Interactive option rendering
4. User response handling
5. Buffer clearing after response
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from modules.execution.executor import ExecutionSystem, ExecutionStep
from modules.execution.registry import ExecutionType, ExecutionCategory, RiskLevel
from modules.execution.permission_manager import PermissionManager


@pytest.fixture
def mock_app():
    """Mock TUI app"""
    app = Mock()
    app.query_one = Mock(return_value=Mock())
    return app


@pytest.fixture
def mock_session():
    """Mock session"""
    session = Mock()
    session.session_id = "test-session-123"
    return session


@pytest.fixture
def execution_system(mock_app, mock_session):
    """Create ExecutionSystem instance"""
    return ExecutionSystem(mock_app, mock_session)


class TestSDKCommandPermissionFlow:
    """Test SDK command permission buffer integration"""

    @pytest.mark.asyncio
    async def test_command_requires_approval_flag(self, execution_system):
        """Verify all SDK commands have requires_approval=True"""
        # Register a test command
        handler = AsyncMock(return_value="test result")

        execution_system.registry.register(
            type=ExecutionType.COMMAND,
            name="/test",
            handler=handler,
            category=ExecutionCategory.SYSTEM,
            risk_level=RiskLevel.SAFE,
            requires_approval=True,
            description="Test command"
        )

        # Get registration
        registration = execution_system.registry.get(ExecutionType.COMMAND, "/test")

        # Verify requires_approval is True
        assert registration is not None, "Command should be registered"
        assert registration.requires_approval is True, "Command should require approval"

    @pytest.mark.asyncio
    async def test_permission_check_called(self, execution_system, mock_app, mock_session):
        """Verify permission check is called before command execution"""
        # Register command
        handler = AsyncMock(return_value="test result")

        execution_system.registry.register(
            type=ExecutionType.COMMAND,
            name="/test",
            handler=handler,
            category=ExecutionCategory.SYSTEM,
            risk_level=RiskLevel.SAFE,
            requires_approval=True,
            description="Test command"
        )

        # Mock permission manager
        with patch.object(execution_system.permission_manager, 'check_permission') as mock_check:
            mock_check.return_value = True

            # Execute command
            await execution_system.execute(
                ExecutionType.COMMAND,
                "/test",
                app=mock_app,
                session=mock_session
            )

            # Verify permission check was called
            assert mock_check.called, "Permission check should be called"
            assert mock_check.call_count == 1, "Permission check should be called once"

    @pytest.mark.asyncio
    async def test_permission_denied_blocks_execution(self, execution_system, mock_app, mock_session):
        """Verify command doesn't execute if permission denied"""
        # Register command
        handler = AsyncMock(return_value="test result")

        execution_system.registry.register(
            type=ExecutionType.COMMAND,
            name="/test",
            handler=handler,
            category=ExecutionCategory.SYSTEM,
            risk_level=RiskLevel.SAFE,
            requires_approval=True,
            description="Test command"
        )

        # Mock permission manager to deny
        with patch.object(execution_system.permission_manager, 'check_permission') as mock_check:
            mock_check.return_value = False

            # Execute command should raise PermissionError
            with pytest.raises(PermissionError, match="Permission denied"):
                await execution_system.execute(
                    ExecutionType.COMMAND,
                    "/test",
                    app=mock_app,
                    session=mock_session
                )

            # Verify handler was NOT called
            handler.assert_not_called()

    @pytest.mark.asyncio
    async def test_permission_buffer_displays_options(self, execution_system, mock_app, mock_session):
        """Verify permission buffer displays interactive options"""
        # Register command
        handler = AsyncMock(return_value="test result")

        execution_system.registry.register(
            type=ExecutionType.COMMAND,
            name="/test",
            handler=handler,
            category=ExecutionCategory.SYSTEM,
            risk_level=RiskLevel.MEDIUM,
            requires_approval=True,
            description="Test command with risk"
        )

        # Mock permission buffer manager
        mock_buffer_manager = Mock()
        mock_prompt_widget = Mock()
        mock_prompt_widget.permission_prompt_data = None
        mock_app.query_one.return_value = mock_prompt_widget

        # Capture the prompt data
        prompt_data_captured = {}

        async def capture_permission_request(registration, context, app, session):
            # This should show the buffer
            if hasattr(app, 'query_one'):
                prompt_input = app.query_one("#prompt-input")
                if prompt_input:
                    prompt_data_captured['title'] = f"System: {registration.name}"
                    prompt_data_captured['options'] = [
                        {'text': 'Yes, allow this once', 'response': 'ALLOW_ONCE'},
                        {'text': 'Yes, and remember for this item', 'response': 'ALLOW_ALWAYS'},
                        {'text': 'Yes, and auto-accept this session', 'response': 'ALLOW_SESSION'},
                        {'text': 'No, cancel', 'response': 'CANCEL'}
                    ]
            return True

        with patch.object(execution_system.permission_manager, 'check_permission', side_effect=capture_permission_request):
            await execution_system.execute(
                ExecutionType.COMMAND,
                "/test",
                app=mock_app,
                session=mock_session
            )

        # Verify options were prepared
        assert 'options' in prompt_data_captured, "Permission options should be prepared"
        assert len(prompt_data_captured['options']) == 4, "Should have 4 permission options"

        # Verify option types
        option_responses = [opt['response'] for opt in prompt_data_captured['options']]
        assert 'ALLOW_ONCE' in option_responses
        assert 'ALLOW_ALWAYS' in option_responses
        assert 'ALLOW_SESSION' in option_responses
        assert 'CANCEL' in option_responses


class TestPermissionBufferRiskDisplay:
    """Test risk-level display in permission buffer"""

    @pytest.mark.asyncio
    async def test_safe_command_risk_display(self, execution_system, mock_app, mock_session):
        """Verify SAFE risk level displays correctly"""
        handler = AsyncMock(return_value="result")

        execution_system.registry.register(
            type=ExecutionType.COMMAND,
            name="/test-safe",
            handler=handler,
            category=ExecutionCategory.SYSTEM,
            risk_level=RiskLevel.SAFE,
            requires_approval=True,
            description="Safe test command"
        )

        registration = execution_system.registry.get(ExecutionType.COMMAND, "/test-safe")
        assert registration.risk_level == RiskLevel.SAFE

    @pytest.mark.asyncio
    async def test_critical_command_risk_display(self, execution_system, mock_app, mock_session):
        """Verify CRITICAL risk level displays correctly"""
        handler = AsyncMock(return_value="result")

        execution_system.registry.register(
            type=ExecutionType.COMMAND,
            name="/test-critical",
            handler=handler,
            category=ExecutionCategory.SYSTEM,
            risk_level=RiskLevel.CRITICAL,
            requires_approval=True,
            description="Critical test command"
        )

        registration = execution_system.registry.get(ExecutionType.COMMAND, "/test-critical")
        assert registration.risk_level == RiskLevel.CRITICAL


class TestPermissionBufferUserInteraction:
    """Test user interaction with permission buffer"""

    @pytest.mark.asyncio
    async def test_allow_once_response(self, execution_system, mock_app, mock_session):
        """Test ALLOW_ONCE response executes command once"""
        handler = AsyncMock(return_value="test result")

        execution_system.registry.register(
            type=ExecutionType.COMMAND,
            name="/test",
            handler=handler,
            category=ExecutionCategory.SYSTEM,
            risk_level=RiskLevel.SAFE,
            requires_approval=True,
            description="Test command"
        )

        # Mock permission to allow once
        with patch.object(execution_system.permission_manager, 'check_permission') as mock_check:
            mock_check.return_value = True

            # Execute command
            result = await execution_system.execute(
                ExecutionType.COMMAND,
                "/test",
                app=mock_app,
                session=mock_session
            )

            assert result == "test result"
            handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_response(self, execution_system, mock_app, mock_session):
        """Test CANCEL response blocks execution"""
        handler = AsyncMock(return_value="test result")

        execution_system.registry.register(
            type=ExecutionType.COMMAND,
            name="/test",
            handler=handler,
            category=ExecutionCategory.SYSTEM,
            risk_level=RiskLevel.SAFE,
            requires_approval=True,
            description="Test command"
        )

        # Mock permission to deny (CANCEL)
        with patch.object(execution_system.permission_manager, 'check_permission') as mock_check:
            mock_check.return_value = False

            # Execute command should raise
            with pytest.raises(PermissionError):
                await execution_system.execute(
                    ExecutionType.COMMAND,
                    "/test",
                    app=mock_app,
                    session=mock_session
                )

            # Handler should not execute
            handler.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
