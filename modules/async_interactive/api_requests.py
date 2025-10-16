"""
API request handlers for different providers
"""

import httpx
from typing import Dict, List, Optional
from .message_handling import convert_messages_for_anthropic, extract_openrouter_policy_error


async def perform_anthropic_request(
    messages: List[Dict], 
    config: Dict, 
    tools: List[Dict] = None,
    max_tokens: int = 4096
) -> Dict:
    """
    Make request to Anthropic API
    
    Args:
        messages: List of conversation messages
        config: API configuration
        tools: Optional tool definitions
        max_tokens: Maximum tokens to generate
        
    Returns:
        Dict with response data or error
    """
    try:
        # Convert messages to Anthropic format
        system_prompt, anthropic_messages = convert_messages_for_anthropic(messages)
        
        # Prepare request data
        request_data = {
            "model": config["model"],
            "max_tokens": max_tokens,
            "messages": anthropic_messages
        }
        
        if system_prompt:
            request_data["system"] = system_prompt
            
        if tools:
            request_data["tools"] = tools
        
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["baseURL"] + "/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": config.get("apiKey", ""),
                    "anthropic-version": "2023-06-01"
                },
                json=request_data,
                timeout=60.0
            )
            
            if response.status_code == 200:
                return {"status": "success", "data": response.json()}
            else:
                error_data = response.text
                return {"status": "error", "error": f"HTTP {response.status_code}: {error_data}"}
                
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def perform_google_request(
    messages: List[Dict],
    config: Dict,
    tools: List[Dict] = None
) -> Dict:
    """
    Make request to Google Gemini API
    
    Args:
        messages: List of conversation messages  
        config: API configuration
        tools: Optional tool definitions
        
    Returns:
        Dict with response data or error
    """
    try:
        # Convert to Google format
        google_messages = []
        for msg in messages:
            if msg.get('role') == 'user':
                google_messages.append({
                    "role": "user",
                    "parts": [{"text": msg.get('content', '')}]
                })
            elif msg.get('role') == 'assistant':
                google_messages.append({
                    "role": "model", 
                    "parts": [{"text": msg.get('content', '')}]
                })
        
        request_data = {
            "contents": google_messages,
            "generationConfig": {
                "maxOutputTokens": 4096,
                "temperature": 0.7
            }
        }
        
        if tools:
            # Convert tools to Google format if needed
            request_data["tools"] = tools
        
        # Make API request
        async with httpx.AsyncClient() as client:
            api_key = config.get("apiKey", "")
            url = f"{config['baseURL']}/v1beta/models/{config['model']}:generateContent"
            
            response = await client.post(
                url,
                headers={
                    "Content-Type": "application/json",
                },
                params={"key": api_key},
                json=request_data,
                timeout=60.0
            )
            
            if response.status_code == 200:
                return {"status": "success", "data": response.json()}
            else:
                error_data = response.text
                return {"status": "error", "error": f"HTTP {response.status_code}: {error_data}"}
                
    except Exception as e:
        return {"status": "error", "error": str(e)}