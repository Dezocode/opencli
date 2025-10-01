#!/usr/bin/env python3
"""
GitHub Tool for OpenCLI
Uses gh CLI for authenticated GitHub operations
"""

import subprocess
import json
from typing import Dict, Optional


class GitHubTool:
    """Wrapper for gh CLI operations"""

    @staticmethod
    def check_auth() -> Dict:
        """Check if user is authenticated with gh CLI"""
        try:
            result = subprocess.run(
                ['gh', 'auth', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return {
                    'authenticated': True,
                    'status': result.stdout.strip()
                }
            else:
                return {
                    'authenticated': False,
                    'message': 'Not authenticated. Run: gh auth login'
                }
        except FileNotFoundError:
            return {
                'authenticated': False,
                'message': 'gh CLI not installed. Install from: https://cli.github.com'
            }
        except Exception as e:
            return {
                'authenticated': False,
                'message': f'Error checking auth: {str(e)}'
            }

    @staticmethod
    def execute_command(command: str, args: list = None) -> str:
        """Execute gh CLI command"""
        auth_status = GitHubTool.check_auth()
        if not auth_status.get('authenticated'):
            return f"❌ {auth_status.get('message')}"

        try:
            cmd = ['gh', command]
            if args:
                cmd.extend(args)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout if result.stdout else result.stderr
            return output.strip() if output else "Command executed successfully"

        except subprocess.TimeoutExpired:
            return "❌ Command timed out"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    @staticmethod
    def repo_view(repo: Optional[str] = None) -> str:
        """View repository details"""
        args = ['repo', 'view']
        if repo:
            args.append(repo)
        args.append('--json')
        args.append('name,description,url,defaultBranchRef,createdAt,updatedAt,stargazerCount,forkCount,languages')

        result = GitHubTool.execute_command('api', ['graphql', '-f', f'query={_build_repo_query(repo)}'])
        return result

    @staticmethod
    def issue_list(repo: Optional[str] = None, limit: int = 10, state: str = 'open') -> str:
        """List issues"""
        args = ['issue', 'list']
        if repo:
            args.extend(['--repo', repo])
        args.extend(['--limit', str(limit), '--state', state, '--json', 'number,title,state,createdAt,author'])

        return GitHubTool.execute_command('issue', args[1:])

    @staticmethod
    def issue_view(number: int, repo: Optional[str] = None) -> str:
        """View issue details"""
        args = ['issue', 'view', str(number)]
        if repo:
            args.extend(['--repo', repo])
        args.append('--json')
        args.append('number,title,body,state,createdAt,author,comments')

        return GitHubTool.execute_command('issue', args[1:])

    @staticmethod
    def issue_create(title: str, body: str = '', repo: Optional[str] = None) -> str:
        """Create new issue"""
        args = ['issue', 'create', '--title', title]
        if body:
            args.extend(['--body', body])
        if repo:
            args.extend(['--repo', repo])

        return GitHubTool.execute_command('issue', args[1:])

    @staticmethod
    def pr_list(repo: Optional[str] = None, limit: int = 10, state: str = 'open') -> str:
        """List pull requests"""
        args = ['pr', 'list']
        if repo:
            args.extend(['--repo', repo])
        args.extend(['--limit', str(limit), '--state', state, '--json', 'number,title,state,createdAt,author,headRefName'])

        return GitHubTool.execute_command('pr', args[1:])

    @staticmethod
    def pr_view(number: int, repo: Optional[str] = None) -> str:
        """View pull request details"""
        args = ['pr', 'view', str(number)]
        if repo:
            args.extend(['--repo', repo])
        args.append('--json')
        args.append('number,title,body,state,createdAt,author,commits,files,reviews')

        return GitHubTool.execute_command('pr', args[1:])

    @staticmethod
    def pr_create(title: str, body: str = '', base: str = 'main', head: Optional[str] = None, repo: Optional[str] = None) -> str:
        """Create pull request"""
        args = ['pr', 'create', '--title', title, '--base', base]
        if body:
            args.extend(['--body', body])
        if head:
            args.extend(['--head', head])
        if repo:
            args.extend(['--repo', repo])

        return GitHubTool.execute_command('pr', args[1:])

    @staticmethod
    def pr_checkout(number: int, repo: Optional[str] = None) -> str:
        """Checkout pull request locally"""
        args = ['pr', 'checkout', str(number)]
        if repo:
            args.extend(['--repo', repo])

        return GitHubTool.execute_command('pr', args[1:])

    @staticmethod
    def workflow_list(repo: Optional[str] = None) -> str:
        """List GitHub Actions workflows"""
        args = ['workflow', 'list']
        if repo:
            args.extend(['--repo', repo])
        args.append('--json')
        args.append('name,state,id,path')

        return GitHubTool.execute_command('workflow', args[1:])

    @staticmethod
    def workflow_run(workflow: str, repo: Optional[str] = None) -> str:
        """Trigger workflow run"""
        args = ['workflow', 'run', workflow]
        if repo:
            args.extend(['--repo', repo])

        return GitHubTool.execute_command('workflow', args[1:])

    @staticmethod
    def run_list(repo: Optional[str] = None, limit: int = 10) -> str:
        """List workflow runs"""
        args = ['run', 'list']
        if repo:
            args.extend(['--repo', repo])
        args.extend(['--limit', str(limit), '--json', 'databaseId,name,status,conclusion,createdAt,headBranch'])

        return GitHubTool.execute_command('run', args[1:])

    @staticmethod
    def gist_create(files: dict, description: str = '', public: bool = True) -> str:
        """Create gist from files"""
        args = ['gist', 'create']
        if description:
            args.extend(['--desc', description])
        if public:
            args.append('--public')
        else:
            args.append('--secret')

        # Add file arguments
        for filename, content in files.items():
            args.extend(['-f', f'{filename}={content}'])

        return GitHubTool.execute_command('gist', args[1:])


def _build_repo_query(repo: Optional[str]) -> str:
    """Build GraphQL query for repo info"""
    # Simplified - would need full implementation
    return '{viewer{login}}'


# Tool execution functions for OpenCLI integration
def execute_github_tool(action: str, **kwargs) -> str:
    """Execute GitHub tool action"""

    # Map actions to methods
    actions = {
        'auth_status': lambda: json.dumps(GitHubTool.check_auth(), indent=2),
        'repo_view': lambda: GitHubTool.repo_view(kwargs.get('repo')),
        'issue_list': lambda: GitHubTool.issue_list(
            kwargs.get('repo'),
            kwargs.get('limit', 10),
            kwargs.get('state', 'open')
        ),
        'issue_view': lambda: GitHubTool.issue_view(
            kwargs.get('number'),
            kwargs.get('repo')
        ),
        'issue_create': lambda: GitHubTool.issue_create(
            kwargs.get('title'),
            kwargs.get('body', ''),
            kwargs.get('repo')
        ),
        'pr_list': lambda: GitHubTool.pr_list(
            kwargs.get('repo'),
            kwargs.get('limit', 10),
            kwargs.get('state', 'open')
        ),
        'pr_view': lambda: GitHubTool.pr_view(
            kwargs.get('number'),
            kwargs.get('repo')
        ),
        'pr_create': lambda: GitHubTool.pr_create(
            kwargs.get('title'),
            kwargs.get('body', ''),
            kwargs.get('base', 'main'),
            kwargs.get('head'),
            kwargs.get('repo')
        ),
        'pr_checkout': lambda: GitHubTool.pr_checkout(
            kwargs.get('number'),
            kwargs.get('repo')
        ),
        'workflow_list': lambda: GitHubTool.workflow_list(kwargs.get('repo')),
        'workflow_run': lambda: GitHubTool.workflow_run(
            kwargs.get('workflow'),
            kwargs.get('repo')
        ),
        'run_list': lambda: GitHubTool.run_list(
            kwargs.get('repo'),
            kwargs.get('limit', 10)
        ),
        'gist_create': lambda: GitHubTool.gist_create(
            kwargs.get('files', {}),
            kwargs.get('description', ''),
            kwargs.get('public', True)
        )
    }

    if action not in actions:
        return f"❌ Unknown GitHub action: {action}\nAvailable: {', '.join(actions.keys())}"

    try:
        return actions[action]()
    except Exception as e:
        return f"❌ Error executing {action}: {str(e)}"
