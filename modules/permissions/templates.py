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