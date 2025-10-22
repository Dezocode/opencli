"""
Test permission prompt focus fix using call_after_refresh

This test verifies that:
1. Permission prompt data is set correctly
2. Focus is scheduled via call_after_refresh (not set immediately)
3. The widget can receive key events after focus is set
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from modules.input_widget.widget import MultiLineInput


class TestPermissionPromptFocus:
    """Test that permission prompt gets focus properly"""

    def test_watch_permission_prompt_uses_call_after_refresh(self):
        """Verify that watch_permission_prompt_data uses call_after_refresh for focus"""
        # Create widget
        widget = MultiLineInput(placeholder="Test")
        widget.refresh = Mock()
        widget.call_after_refresh = Mock()
        
        # Mock the app property using PropertyMock
        mock_app = Mock()
        with patch.object(type(widget), 'app', new_callable=PropertyMock) as mock_app_prop:
            mock_app_prop.return_value = mock_app
            
            # Set permission prompt data (triggers watcher)
            prompt_data = {
                'title': 'Test Permission',
                'message': 'Allow test operation?',
                'options': [
                    {'text': 'Allow', 'value': 'allow'},
                    {'text': 'Deny', 'value': 'deny'}
                ],
                'selected': 0
            }

            # Trigger the watcher directly (simulating reactive property change)
            widget.watch_permission_prompt_data(None, prompt_data)

            # Verify refresh was called
            assert widget.refresh.called, "Widget should call refresh()"

            # Verify call_after_refresh was called to schedule focus
            assert widget.call_after_refresh.called, "Should use call_after_refresh to schedule focus"

            # Get the callback function that was passed to call_after_refresh
            callback = widget.call_after_refresh.call_args[0][0]
            assert callable(callback), "Callback should be a function"

            # Execute the callback to verify it sets focus
            callback()

            # Verify app.set_focus was called
            assert mock_app.set_focus.called, "Should call app.set_focus in callback"
            assert mock_app.set_focus.call_args[0][0] == widget, "Should focus on self"

    def test_permission_selected_option_initialized(self):
        """Verify selected option is initialized from prompt data"""
        widget = MultiLineInput(placeholder="Test")
        widget.refresh = Mock()
        widget.call_after_refresh = Mock()

        prompt_data = {
            'title': 'Test Permission',
            'options': [
                {'text': 'Option 1', 'value': '1'},
                {'text': 'Option 2', 'value': '2'}
            ],
            'selected': 1  # Start at second option
        }

        # Trigger the watcher
        widget.watch_permission_prompt_data(None, prompt_data)

        # Verify selected option was initialized
        assert widget.permission_selected_option == 1, "Should initialize selected option from prompt data"

    def test_no_call_after_refresh_when_clearing_prompt(self):
        """Verify refresh is called when clearing permission prompt"""
        widget = MultiLineInput(placeholder="Test")
        widget.refresh = Mock()
        widget.call_after_refresh = Mock()
        widget.permission_prompt_data = {'title': 'Test'}

        # Clear permission prompt (set to None)
        widget.watch_permission_prompt_data({'title': 'Test'}, None)

        # Verify refresh was still called
        assert widget.refresh.called, "Should still refresh when clearing"

    def test_on_blur_prevents_focus_loss_during_permission(self):
        """Verify widget prevents losing focus during permission prompt"""
        widget = MultiLineInput(placeholder="Test")
        widget.permission_prompt_data = {
            'title': 'Test Permission',
            'options': []
        }
        widget.refresh = Mock()
        widget.focus = Mock()
        
        # Mock the app property
        mock_app = Mock()
        with patch.object(type(widget), 'app', new_callable=PropertyMock) as mock_app_prop:
            mock_app_prop.return_value = mock_app

            # Simulate blur event
            widget.on_blur()

            # Verify focus was re-grabbed
            assert mock_app.set_focus.called, \
                "Should re-grab focus when blur occurs during permission prompt"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
