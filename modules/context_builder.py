#!/usr/bin/env python3
"""
Context Builder for OpenCLI Agent System
Efficiently builds and caches agent contexts to minimize token usage
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime


class ContextBuilder:
    """Builds and caches context for agents with hash-based invalidation"""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.contexts_dir = config_dir / "agents" / "contexts"
        self.temp_dir = config_dir / "agents" / "temp"
        self.cache_file = self.contexts_dir / "agents_md_cache.json"
        self.project_contexts_dir = self.contexts_dir / "project_contexts"

        # Ensure directories exist
        self.contexts_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.project_contexts_dir.mkdir(parents=True, exist_ok=True)

    def find_agents_md(self, working_dir: str = None) -> Optional[Tuple[str, str]]:
        """
        Find AGENTS.md file and return (content, file_path)
        Walks up directory tree from working_dir
        """
        if working_dir:
            current = Path(working_dir)
            for parent in [current] + list(current.parents):
                agents_file = parent / 'AGENTS.md'
                if agents_file.exists():
                    try:
                        with open(agents_file) as f:
                            content = f.read()
                        return content, str(agents_file)
                    except:
                        pass

        # Fallback to current directory
        if Path('AGENTS.md').exists():
            try:
                with open('AGENTS.md') as f:
                    content = f.read()
                return content, str(Path('AGENTS.md').absolute())
            except:
                pass

        # Final fallback to the default template shipped with the agent system
        default_agents_md = self.config_dir / 'agents' / 'system_prompts' / 'base' / 'AGENTS.md'
        if default_agents_md.exists():
            try:
                with open(default_agents_md) as f:
                    content = f.read()
                return content, str(default_agents_md)
            except:
                pass

        return None

    def get_agents_md_hash(self, content: str) -> str:
        """Generate hash of AGENTS.md content"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def load_cache(self) -> Dict:
        """Load AGENTS.md cache"""
        if not self.cache_file.exists():
            return {}

        try:
            with open(self.cache_file) as f:
                return json.load(f)
        except:
            return {}

    def save_cache(self, cache: Dict):
        """Save AGENTS.md cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save cache: {e}")

    def get_project_id(self, file_path: str) -> str:
        """Generate project ID from AGENTS.md file path"""
        # Use parent directory name as project ID
        return Path(file_path).parent.name

    def build_context(
        self,
        agent_name: str,
        agent_system_prompt: str,
        working_dir: str = None,
        force_rebuild: bool = False
    ) -> Tuple[str, bool]:
        """
        Build context for agent with caching
        Returns: (context_text, was_cached)
        """
        # Find AGENTS.md
        agents_md_result = self.find_agents_md(working_dir)

        # Get CLI environment info
        cli_environment = self._get_cli_environment()

        if not agents_md_result:
            # No AGENTS.md, return agent system prompt + CLI env
            return f"{agent_system_prompt}\n\n{cli_environment}", False

        agents_md_content, agents_md_path = agents_md_result

        # Include CLI environment in hash to detect tool changes
        combined_content = f"{agents_md_content}\n{cli_environment}"
        content_hash = self.get_agents_md_hash(combined_content)
        project_id = self.get_project_id(agents_md_path)

        # Load cache
        cache = self.load_cache()
        cache_key = f"{project_id}_{agent_name}_{content_hash}"

        # Check if cached version exists AND is one of the latest 5
        if not force_rebuild and cache_key in cache:
            cached_data = cache[cache_key]
            cached_file = Path(cached_data.get('file'))

            # Verify this is in the latest 5 contexts
            if cached_file.exists() and self._is_recent_context(cache, cache_key, limit=5):
                try:
                    with open(cached_file) as f:
                        compiled_context = f.read()
                    return compiled_context, True
                except:
                    pass

        # Build new context with CLI environment
        compiled_context = self._compile_context(
            agent_system_prompt,
            agents_md_content,
            agents_md_path,
            working_dir,
            cli_environment
        )

        # Save to temp file
        temp_file = self.temp_dir / f"compiled_{agent_name}_{content_hash}.txt"
        try:
            with open(temp_file, 'w') as f:
                f.write(compiled_context)

            # Update cache
            cache[cache_key] = {
                'file': str(temp_file),
                'created': datetime.now().isoformat(),
                'project_id': project_id,
                'agent': agent_name,
                'hash': content_hash
            }
            self.save_cache(cache)

            # Cleanup old cache entries (keep last 5 total)
            self._cleanup_old_contexts(cache, keep_latest=5)

        except Exception as e:
            print(f"Warning: Failed to cache context: {e}")

        return compiled_context, False

    def _compile_context(
        self,
        agent_prompt: str,
        agents_md: str,
        agents_md_path: str,
        working_dir: str,
        cli_environment: str
    ) -> str:
        """Compile full context from components"""
        parts = [agent_prompt]

        # Add CLI environment section
        parts.append(f"\n{cli_environment}")

        # Add AGENTS.md section
        parts.append("\n## Project Context (from AGENTS.md)")
        parts.append(f"Source: {agents_md_path}")
        parts.append(f"\n{agents_md}")

        # Add working directory info
        if working_dir:
            parts.append(f"\n## Working Directory")
            parts.append(f"{working_dir}")

        return '\n'.join(parts)

    def _get_cli_environment(self) -> str:
        """Get CLI environment information including available tools"""
        import subprocess

        parts = ["## CLI Environment"]

        # Get available tools from ~/bin (symlinked tools)
        bin_dir = Path.home() / "bin"
        if bin_dir.exists():
            try:
                # List executables in ~/bin
                tools = []
                for item in bin_dir.iterdir():
                    if item.is_file() or item.is_symlink():
                        # Check if executable
                        if os.access(item, os.X_OK):
                            # Get symlink target if applicable
                            if item.is_symlink():
                                target = item.resolve()
                                tools.append(f"  - {item.name} → {target}")
                            else:
                                tools.append(f"  - {item.name}")

                if tools:
                    parts.append("\n### Available CLI Tools (~/bin)")
                    parts.extend(sorted(tools))
            except Exception as e:
                parts.append(f"\n### Available CLI Tools: Error listing ({e})")

        # Get shell info
        shell = os.getenv('SHELL', 'unknown')
        parts.append(f"\n### Shell: {shell}")

        # Get platform
        import platform
        parts.append(f"### Platform: {platform.system()} {platform.release()}")

        # Get Python version
        import sys
        parts.append(f"### Python: {sys.version.split()[0]}")

        # List OpenCLI built-in tools
        parts.append("\n### OpenCLI Built-in Tools")
        parts.append("  - Read: Read file contents")
        parts.append("  - Write: Write to file")
        parts.append("  - Edit: Edit file with string replacement")
        parts.append("  - Bash: Execute shell commands")
        parts.append("  - Glob: Find files by pattern")
        parts.append("  - Grep: Search file contents")
        parts.append("  - GitHub: Interact with GitHub via gh CLI")

        return '\n'.join(parts)

    def _is_recent_context(self, cache: Dict, cache_key: str, limit: int = 5) -> bool:
        """Check if cache_key is in the most recent N contexts"""
        # Sort all cache entries by creation time
        sorted_entries = sorted(
            cache.items(),
            key=lambda x: x[1].get('created', ''),
            reverse=True
        )

        # Get the latest N keys
        recent_keys = [key for key, _ in sorted_entries[:limit]]

        return cache_key in recent_keys

    def _cleanup_old_contexts(self, cache: Dict, keep_latest: int = 5):
        """Keep only the latest N context files, delete older ones"""
        # Sort ALL cache entries by creation time (not per-project)
        sorted_entries = sorted(
            cache.items(),
            key=lambda x: x[1].get('created', ''),
            reverse=True
        )

        # Keep the latest N, remove the rest
        entries_to_remove = sorted_entries[keep_latest:]

        for key, data in entries_to_remove:
            # Delete temp file
            temp_file = Path(data.get('file'))
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as e:
                    print(f"Warning: Failed to delete old context file {temp_file}: {e}")

            # Remove from cache
            if key in cache:
                del cache[key]

        # Save updated cache if we removed anything
        if entries_to_remove:
            self.save_cache(cache)

    def create_session_context_file(self, session_id: str, context: str) -> Path:
        """Create temporary context file for session"""
        temp_file = self.temp_dir / f"context_{session_id}.txt"

        try:
            with open(temp_file, 'w') as f:
                f.write(context)
            return temp_file
        except Exception as e:
            print(f"Warning: Failed to create session context file: {e}")
            return None

    def cleanup_old_temp_files(self, max_age_hours: int = 24):
        """
        Clean up temp files older than specified hours
        NOTE: This is only for session temp files, not compiled contexts.
        Compiled contexts are managed by _cleanup_old_contexts() with 5-file limit.
        """
        import time
        cutoff_time = time.time() - (max_age_hours * 3600)

        # Only clean up context_*.txt files (session files), not compiled_*.txt
        for temp_file in self.temp_dir.glob("context_*.txt"):
            try:
                if temp_file.stat().st_mtime < cutoff_time:
                    temp_file.unlink()
            except:
                pass

    def invalidate_cache(self, project_id: str = None):
        """Invalidate cache for project or all projects"""
        cache = self.load_cache()

        if project_id:
            # Invalidate specific project
            keys_to_remove = [
                key for key, data in cache.items()
                if data.get('project_id') == project_id
            ]
        else:
            # Invalidate all
            keys_to_remove = list(cache.keys())

        for key in keys_to_remove:
            data = cache[key]
            temp_file = Path(data.get('file'))
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
            del cache[key]

        self.save_cache(cache)

    def get_cache_stats(self) -> Dict:
        """Get statistics about cached contexts"""
        cache = self.load_cache()

        stats = {
            'total_entries': len(cache),
            'projects': {},
            'agents': {}
        }

        for data in cache.values():
            project_id = data.get('project_id', 'unknown')
            agent = data.get('agent', 'unknown')

            stats['projects'][project_id] = stats['projects'].get(project_id, 0) + 1
            stats['agents'][agent] = stats['agents'].get(agent, 0) + 1

        return stats
