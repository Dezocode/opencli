"""
Model selection and management handlers for OpenCLI TUI
Extracted from simple_tui.py to handle model browser, local models, etc.
"""

import asyncio
from typing import Dict, List, Any

try:
    from modules.permissions import PermissionResponse
except ImportError:
    try:
        import importlib
        perm_prompt = importlib.import_module('modules.permissions')
        PermissionResponse = perm_prompt.PermissionResponse
    except:
        PermissionResponse = None


class ModelHandlers:
    """Mixin class containing model-related handlers and workflows"""

    async def _handle_local_model_step(self, current_step: str, option_data: dict) -> None:
        """Handle multi-step local model selection workflow"""
        if not PermissionResponse:
            return

        # Get context
        if not hasattr(self.session, '_local_context'):
            self.write("\n[red]✗ Context lost[/red]\n\n")
            return

        ctx = self.session._local_context
        recs = ctx['recs']
        is_installed = ctx['is_installed']

        # Clear current prompt
        try:
            prompt_input = self.query_one("#prompt-input")
            self._clear_permission_prompt()
            prompt_input.refresh()
        except Exception:
            pass

        # STEP 1: Setup type selected
        if current_step == 'setup_type':
            await self._handle_setup_type_selection(option_data, recs, is_installed)
        # STEP 2a: Single model selected
        elif current_step == 'single_model_select':
            await self._handle_single_model_selection(option_data)
        # STEP 2b: Planner selected for dual
        elif current_step == 'planner_select':
            await self._handle_planner_selection(option_data, recs, is_installed)
        # STEP 3: Coder selected for dual
        elif current_step == 'coder_select':
            await self._handle_coder_selection(option_data)

    async def _handle_setup_type_selection(self, option_data: dict, recs: dict, is_installed) -> None:
        """Handle setup type selection (existing/single/dual)"""
        setup_type = option_data.get('setup_type')
        self.session._local_selections['setup_type'] = setup_type

        if setup_type == 'existing':
            # User selected an existing installed model
            model_name = option_data.get('model', '')
            self.session._awaiting_local_model_selection = False

            self.write(f"\n[green]✓ Selected {model_name}[/green]\n\n")
            self.write("[dim]Configure Ollama as a provider:[/dim]\n")
            self.write(f"  1. Run [cyan]/providers add ollama[/cyan]\n")
            self.write(f"  2. Use [cyan]/model[/cyan] to see your Ollama models\n")
            self.write(f"  3. Select [cyan]{model_name}[/cyan] from the list\n\n")

            self._cleanup_local_model_state()

        elif setup_type == 'single':
            await self._show_single_model_options(recs, is_installed)

        elif setup_type == 'dual':
            await self._show_dual_model_planner_options(recs, is_installed)

    async def _show_single_model_options(self, recs: dict, is_installed) -> None:
        """Show single model selection options"""
        self.write("\n[cyan]▸ Single model setup selected[/cyan]\n\n")

        # Build single model options
        options = []
        primary = recs['single_model']['primary']
        primary_installed = is_installed(primary['name'])

        options.append({
            'text': f"{primary['name']} - Recommended" + (" [green]✓ Installed[/green]" if primary_installed else ""),
            'response': PermissionResponse.ALLOW_ONCE,
            'data': {
                'model': primary['name'],
                'pull_command': f"ollama pull {primary['name']}",
                'installed': primary_installed
            }
        })

        # Alternative if exists
        if 'alternative' in recs['single_model']:
            alt = recs['single_model']['alternative']
            alt_installed = is_installed(alt['name'])
            options.append({
                'text': f"{alt['name']} - Alternative" + (" [green]✓ Installed[/green]" if alt_installed else ""),
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {
                    'model': alt['name'],
                    'pull_command': f"ollama pull {alt['name']}",
                    'installed': alt_installed
                }
            })

        options.append({'text': 'Back', 'response': PermissionResponse.CANCEL})

        prompt_data = {
            'title': 'Select Single Model',
            'message': 'Choose which model to install:',
            'details': {},
            'options': options
        }

        # Show permission prompt
        try:
            prompt_input = self.query_one("#prompt-input")
            prompt_data['selected'] = 0
            prompt_input.permission_prompt_data = prompt_data
            prompt_input.refresh()
            self.session._local_step = 'single_model_select'
        except Exception:
            pass

    async def _show_dual_model_planner_options(self, recs: dict, is_installed) -> None:
        """Show dual model planner selection options"""
        self.write("\n[cyan]▸ Dual model setup selected[/cyan]\n\n")

        # Build planner options
        options = []
        for model in recs['dual_model']['planners']:
            model_installed = is_installed(model['name'])
            options.append({
                'text': f"{model['name']}" + (" [green]✓ Installed[/green]" if model_installed else ""),
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {
                    'model': model['name'],
                    'pull_command': f"ollama pull {model['name']}",
                    'installed': model_installed
                }
            })

        options.append({'text': 'Back', 'response': PermissionResponse.CANCEL})

        prompt_data = {
            'title': 'Select Planner Model',
            'message': 'Choose the planner model (for reasoning and planning):',
            'details': {},
            'options': options
        }

        # Show permission prompt
        try:
            prompt_input = self.query_one("#prompt-input")
            prompt_data['selected'] = 0
            prompt_input.permission_prompt_data = prompt_data
            prompt_input.refresh()
            self.session._local_step = 'planner_select'
        except Exception:
            pass

    async def _handle_single_model_selection(self, option_data: dict) -> None:
        """Handle single model selection and execute installation"""
        model_name = option_data.get('model', '')
        pull_command = option_data.get('pull_command', '')
        installed = option_data.get('installed', False)

        self.session._awaiting_local_model_selection = False

        if installed:
            self.write(f"\n[green]✓ {model_name} is already installed[/green]\n\n")
        else:
            self.write(f"\n[yellow]⋯ Installing {model_name}...[/yellow]\n")
            # Here you would execute the pull command
            self.write(f"[dim]Running: {pull_command}[/dim]\n\n")

        self._cleanup_local_model_state()

    async def _handle_planner_selection(self, option_data: dict, recs: dict, is_installed) -> None:
        """Handle planner model selection and show coder options"""
        planner_model = option_data.get('model', '')
        self.session._local_selections['planner'] = planner_model

        self.write(f"\n[green]✓ Planner: {planner_model}[/green]\n\n")

        # Show coder selection
        self.write("[cyan]▸ Now select a coder model[/cyan]\n\n")

        options = []
        for model in recs['dual_model']['coders']:
            model_installed = is_installed(model['name'])
            options.append({
                'text': f"{model['name']}" + (" [green]✓ Installed[/green]" if model_installed else ""),
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {
                    'model': model['name'],
                    'pull_command': f"ollama pull {model['name']}",
                    'installed': model_installed
                }
            })

        options.append({'text': 'Back', 'response': PermissionResponse.CANCEL})

        prompt_data = {
            'title': 'Select Coder Model',
            'message': 'Choose the coder model (for implementation):',
            'details': {},
            'options': options
        }

        # Show permission prompt
        try:
            prompt_input = self.query_one("#prompt-input")
            prompt_data['selected'] = 0
            prompt_input.permission_prompt_data = prompt_data
            prompt_input.refresh()
            self.session._local_step = 'coder_select'
        except Exception:
            pass

    async def _handle_coder_selection(self, option_data: dict) -> None:
        """Handle coder model selection and execute dual setup"""
        coder_model = option_data.get('model', '')
        self.session._local_selections['coder'] = coder_model

        self.session._awaiting_local_model_selection = False

        # Get both selections
        planner = self.session._local_selections.get('planner', '')
        coder = coder_model

        self.write(f"\n[green]✓ Dual model setup complete![/green]\n")
        self.write(f"  Planner: [cyan]{planner}[/cyan]\n")
        self.write(f"  Coder: [cyan]{coder}[/cyan]\n\n")

        self.write("[dim]Both models will be installed if not already present.[/dim]\n\n")

        # Here you would execute the installation commands for both models
        self._cleanup_local_model_state()

    def show_model_browser(self) -> None:
        """Show the Ollama model browser"""
        # Check if Ollama is available
        is_ollama_running = self._check_ollama_status()
        
        # Get popular models (this would typically come from an API)
        model_options = self._get_popular_models()

        prompt_data = {
            'title': 'Ollama Model Browser',
            'message': f'Select a model to pull and install:\n\nOllama Status: {"✓ Running in Docker" if is_ollama_running else "Not running"}\n\nModels sorted by popularity:',
            'options': model_options
        }

        # Show permission prompt
        try:
            prompt_input = self.query_one("#prompt-input")
            prompt_data['selected'] = 0
            prompt_input.permission_prompt_data = prompt_data
            prompt_input.refresh()

            # Set flag to handle response
            self.session._awaiting_model_browser_selection = True
        except Exception as e:
            self.write(f"[red]✗ Could not show model browser: {e}[/red]\n\n")

    def _check_ollama_status(self) -> bool:
        """Check if Ollama is running"""
        try:
            import subprocess
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            return 'ollama' in result.stdout.lower()
        except:
            return False

    def _get_popular_models(self) -> List[Dict[str, Any]]:
        """Get list of popular models for the browser"""
        # This would typically fetch from Ollama API or a curated list
        popular_models = [
            {"name": "llama3.2:3b", "size": "2.0GB", "description": "Fast, efficient model"},
            {"name": "llama3.2:1b", "size": "1.3GB", "description": "Ultra-fast, minimal model"},
            {"name": "qwen2.5:7b", "size": "4.7GB", "description": "Excellent coding model"},
            {"name": "llama3.1:8b", "size": "4.7GB", "description": "Balanced performance"},
            {"name": "codellama:7b", "size": "3.8GB", "description": "Specialized for code"},
        ]

        options = []
        for model in popular_models:
            options.append({
                'text': f"{model['name']} ({model['size']}) - {model['description']}",
                'response': PermissionResponse.ALLOW_ONCE,
                'data': {
                    'model_name': model['name'],
                    'size': model['size'],
                    'description': model['description']
                }
            })

        options.append({'text': 'Cancel', 'response': PermissionResponse.CANCEL})
        return options

    def _cleanup_local_model_state(self) -> None:
        """Clean up local model selection state"""
        if hasattr(self.session, '_local_context'):
            del self.session._local_context
        if hasattr(self.session, '_local_step'):
            del self.session._local_step
        if hasattr(self.session, '_local_selections'):
            del self.session._local_selections