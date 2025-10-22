"""Permission prompt templates and builders"""

from typing import Dict, List, Any
from pathlib import Path
from .enums import PermissionResponse


class PermissionTemplates:
    """Templates for different types of permission prompts"""
    
    @staticmethod
    def create_file_permission_prompt(
        file_path: str,
        operation: str,
        risk_level: str = "medium",
        details: str = None
    ) -> Dict[str, Any]:
        """Create a file operation permission prompt"""
        
        prompt_data = {
            'type': 'file_operation',
            'title': f'File {operation.title()} Permission',
            'message': f'Allow {operation} operation on file?',
            'details': {
                'file_path': file_path,
                'operation': operation,
                'risk_level': risk_level
            },
            'options': []
        }
        
        if details:
            prompt_data['details']['additional_info'] = details
        
        # Standard file operation options
        prompt_data['options'] = [
            {
                'text': 'Allow Once',
                'label': 'Allow Once',
                'response': PermissionResponse.ALLOW_ONCE
            },
            {
                'text': 'Allow for Domain',
                'label': 'Allow for Domain',
                'description': f'Allow all {operation} operations in this directory',
                'response': PermissionResponse.ALLOW_DOMAIN,
                'domain': str(Path(file_path).parent)
            },
            {
                'text': 'Deny',
                'label': 'Deny',
                'response': PermissionResponse.DENY
            }
        ]
        
        return prompt_data
    
    @staticmethod
    def create_bash_permission_prompt(
        command: str,
        risk_level: str = "medium",
        estimated_duration: str = None,
        working_directory: str = None
    ) -> Dict[str, Any]:
        """Create a bash command permission prompt"""
        
        prompt_data = {
            'type': 'bash_command',
            'title': 'Bash Command Permission',
            'message': 'Allow execution of bash command?',
            'details': {
                'command': command,
                'risk_level': risk_level
            },
            'options': []
        }
        
        if estimated_duration:
            prompt_data['details']['estimated_duration'] = estimated_duration
        if working_directory:
            prompt_data['details']['working_directory'] = working_directory
        
        # Bash command options
        prompt_data['options'] = [
            {
                'text': 'Allow Once',
                'label': 'Allow Once',
                'response': PermissionResponse.ALLOW_ONCE
            },
            {
                'text': 'Allow Always',
                'label': 'Allow Always',
                'description': 'Allow this exact command permanently',
                'response': PermissionResponse.ALLOW_ALWAYS,
            },
            {
                'text': 'Deny',
                'label': 'Deny',
                'response': PermissionResponse.DENY
            }
        ]
        
        return prompt_data
    
    @staticmethod
    def create_api_permission_prompt(
        api_name: str,
        endpoint: str = None,
        estimated_cost: str = None,
        data_details: str = None
    ) -> Dict[str, Any]:
        """Create an API operation permission prompt"""
        
        prompt_data = {
            'type': 'api_operation',
            'title': f'{api_name} API Permission',
            'message': f'Allow API call to {api_name}?',
            'details': {
                'api_name': api_name,
                'risk_level': 'low'
            },
            'options': []
        }
        
        if endpoint:
            prompt_data['details']['endpoint'] = endpoint
        if estimated_cost:
            prompt_data['details']['estimated_cost'] = estimated_cost
        if data_details:
            prompt_data['details']['data_details'] = data_details
        
        # API operation options
        prompt_data['options'] = [
            {
                'text': 'Allow Once',
                'label': 'Allow Once',
                'response': PermissionResponse.ALLOW_ONCE
            },
            {
                'text': 'Allow for Session',
                'label': 'Allow for Session',
                'description': 'Allow for this session only',
                'response': PermissionResponse.ALLOW_SESSION,
            },
            {
                'text': 'Deny',
                'label': 'Deny',
                'response': PermissionResponse.DENY
            }
        ]
        
        return prompt_data
    
    @staticmethod
    def create_tool_permission_prompt(
        tool_name: str,
        tool_args: Dict[str, Any],
        risk_level: str = "medium",
        description: str = None
    ) -> Dict[str, Any]:
        """Create a tool execution permission prompt"""
        
        prompt_data = {
            'type': 'tool_execution',
            'title': f'Tool Execution Permission',
            'message': f'Allow execution of {tool_name} tool?',
            'details': {
                'tool_name': tool_name,
                'tool_args': tool_args,
                'risk_level': risk_level
            },
            'options': []
        }
        
        if description:
            prompt_data['details']['description'] = description
        
        # Tool execution options
        prompt_data['options'] = [
            {
                'text': 'Allow Once',
                'label': 'Allow Once',
                'response': PermissionResponse.ALLOW_ONCE
            },
            {
                'text': 'Allow Always',
                'label': 'Allow Always',
                'description': f'Always allow {tool_name} tool',
                'response': PermissionResponse.ALLOW_ALWAYS,
            },
            {
                'text': 'Deny',
                'label': 'Deny',
                'response': PermissionResponse.DENY
            }
        ]
        
        return prompt_data
    
    @staticmethod
    def create_generic_permission_prompt(
        title: str,
        message: str,
        details: Dict[str, Any] = None,
        options: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a generic permission prompt"""
        
        prompt_data = {
            'type': 'generic',
            'title': title,
            'message': message,
            'details': details or {},
            'options': options or [
                {
                    'text': 'Allow',
                    'label': 'Allow',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': 'Deny',
                    'label': 'Deny',
                    'response': PermissionResponse.DENY
                }
            ]
        }
        
        return prompt_data
    
    # Tool-specific prompts (migrated from async_permissions.py)
    
    @staticmethod
    def file_edit(file_path: str, old_str: str, new_str: str) -> Dict[str, Any]:
        """Create permission prompt for Edit tool"""
        return {
            'title': 'File Edit Permission',
            'message': f'Claude wants to edit a file.\n\n**File:** `{file_path}`\n\nDo you want to allow this?',
            'details': {
                'file_path': file_path,
                'old_string': old_str[:100] + ('...' if len(old_str) > 100 else ''),
                'new_string': new_str[:100] + ('...' if len(new_str) > 100 else ''),
            },
            'options': [
                {
                    'text': 'Yes, allow this edit',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': "Yes, and don't ask again for Edit operations",
                    'response': PermissionResponse.ALLOW_ALWAYS,
                    'data': {'tool': 'Edit'}
                },
                {
                    'text': 'No, skip this operation (esc)',
                    'response': PermissionResponse.DENY
                }
            ]
        }
    
    @staticmethod
    def file_write(file_path: str, content: str) -> Dict[str, Any]:
        """Create permission prompt for Write tool"""
        content_preview = content[:100] + ('...' if len(content) > 100 else '')
        return {
            'title': 'File Write Permission',
            'message': f'Claude wants to write to a file.\n\n**File:** `{file_path}`\n**Content:** ({len(content)} characters)\n\nDo you want to allow this?',
            'details': {
                'file_path': file_path,
                'content_length': len(content),
                'content_preview': content_preview,
            },
            'options': [
                {
                    'text': 'Yes, allow this write',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': "Yes, and don't ask again for Write operations",
                    'response': PermissionResponse.ALLOW_ALWAYS,
                    'data': {'tool': 'Write'}
                },
                {
                    'text': 'No, skip this operation (esc)',
                    'response': PermissionResponse.DENY
                }
            ]
        }
    
    @staticmethod
    def bash_command(command: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create permission prompt for Bash command"""
        message_parts = [f'Claude wants to execute a bash command.\n\n**Command:** `{command}`']
        if description:
            message_parts.append(f'**Description:** {description}')
        message_parts.append('\nDo you want to allow this?')
        
        return {
            'title': 'Bash Command Permission',
            'message': '\n'.join(message_parts),
            'details': {
                'command': command,
                'description': description or 'No description provided',
            },
            'options': [
                {
                    'text': 'Yes, allow this command',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': "Yes, and don't ask again for Bash",
                    'response': PermissionResponse.ALLOW_ALWAYS,
                    'data': {'tool': 'Bash'}
                },
                {
                    'text': 'No, skip this operation (esc)',
                    'response': PermissionResponse.DENY
                }
            ]
        }
    
    @staticmethod
    def webfetch(url: str) -> Dict[str, Any]:
        """Create permission prompt for WebFetch tool"""
        return {
            'title': 'Web Fetch Permission',
            'message': f'Claude wants to fetch content from a URL.\n\n**URL:** `{url}`\n\nDo you want to allow this?',
            'details': {
                'url': url,
            },
            'options': [
                {
                    'text': 'Yes, allow this fetch',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': 'Yes, allow for this domain',
                    'response': PermissionResponse.ALLOW_DOMAIN,
                    'data': {'url': url}
                },
                {
                    'text': "Yes, and don't ask again for WebFetch",
                    'response': PermissionResponse.ALLOW_ALWAYS,
                    'data': {'tool': 'WebFetch'}
                },
                {
                    'text': 'No, skip this operation (esc)',
                    'response': PermissionResponse.DENY
                }
            ]
        }
    
    @staticmethod
    def configure_headers(
        provider: str,
        model: Optional[str] = None,
        issue: Optional[str] = None,
        current_headers: Optional[Dict[str, Any]] = None,
        proposed_headers: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create permission prompt for ConfigureHeaders tool"""
        message_parts = [f'Claude wants to configure API headers.\n\n**Provider:** {provider}']
        if model:
            message_parts.append(f'**Model:** {model}')
        if issue:
            message_parts.append(f'**Issue:** {issue}')
        message_parts.append('\nDo you want to allow this?')
        
        details = {
            'provider': provider,
        }
        if model:
            details['model'] = model
        if issue:
            details['issue'] = issue
        if current_headers:
            details['current_headers'] = current_headers
        if proposed_headers:
            details['proposed_headers'] = proposed_headers
        
        return {
            'title': 'Configure Headers Permission',
            'message': '\n'.join(message_parts),
            'details': details,
            'options': [
                {
                    'text': 'Yes, allow this configuration',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': "Yes, and don't ask again for ConfigureHeaders",
                    'response': PermissionResponse.ALLOW_ALWAYS,
                    'data': {'tool': 'ConfigureHeaders'}
                },
                {
                    'text': 'No, skip this operation (esc)',
                    'response': PermissionResponse.DENY
                }
            ]
        }
    
    @staticmethod
    def code_refactoring(plan: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Create permission prompt for Refactoring tool"""
        return {
            'title': 'Code Refactoring Permission',
            'message': 'Claude wants to perform code refactoring.\n\nDo you want to allow this?',
            'details': {
                'plan': plan,
                'result': result,
            },
            'options': [
                {
                    'text': 'Yes, allow this refactoring',
                    'response': PermissionResponse.ALLOW_ONCE
                },
                {
                    'text': 'Yes, allow for this session',
                    'response': PermissionResponse.ALLOW_SESSION,
                    'data': {'tool': 'Refactoring'}
                },
                {
                    'text': 'No, skip this operation (esc)',
                    'response': PermissionResponse.DENY
                }
            ]
        }