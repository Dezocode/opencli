"""
Client management for async interactive mode
"""

from openai import AsyncOpenAI


def create_async_client(config):
    """
    Factory to create AsyncOpenAI client with provider defaults
    
    Args:
        config: OpenCLI configuration dict with baseURL, apiKey, etc.
        
    Returns:
        AsyncOpenAI: Configured async client
    """
    headers = config.get("defaultHeaders") or None
    
    return AsyncOpenAI(
        base_url=config["baseURL"],
        api_key=config.get("apiKey", ""),
        default_headers=headers
    )