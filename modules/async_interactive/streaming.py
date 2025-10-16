"""
API response streaming handler
Manages streaming responses from various AI providers
"""

import asyncio
import httpx
import json
from typing import Dict, List, Optional, AsyncIterator
from .message_handling import extract_openrouter_policy_error


class StreamHandler:
    """Handles streaming API responses from various providers"""
    
    def __init__(self, buffer_manager=None):
        self.buffer_manager = buffer_manager
        self.interrupted = False
    
    async def stream_openrouter(
        self, 
        messages: List[Dict], 
        config: Dict, 
        tools: List[Dict] = None
    ) -> AsyncIterator[Dict]:
        """
        Stream response from OpenRouter API
        
        Args:
            messages: Conversation messages
            config: API configuration
            tools: Optional tool definitions
            
        Yields:
            Dict with chunk data or error
        """
        try:
            request_data = {
                "model": config["model"],
                "messages": messages,
                "stream": True
            }
            
            if tools:
                request_data["tools"] = tools
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.get('apiKey', '')}"
            }
            
            # Add default headers from config
            if "defaultHeaders" in config:
                headers.update(config["defaultHeaders"])
            
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    config["baseURL"] + "/chat/completions",
                    headers=headers,
                    json=request_data,
                    timeout=60.0
                ) as response:
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        policy_error = extract_openrouter_policy_error(error_text.decode())
                        if policy_error:
                            yield {"type": "error", "error": policy_error}
                        else:
                            yield {"type": "error", "error": f"HTTP {response.status_code}: {error_text.decode()}"}
                        return
                    
                    async for line in response.aiter_lines():
                        if self.interrupted:
                            yield {"type": "interrupted"}
                            return
                            
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                yield {"type": "done"}
                                return
                                
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield {
                                            "type": "content",
                                            "content": delta["content"]
                                        }
                                    if "tool_calls" in delta:
                                        yield {
                                            "type": "tool_call",
                                            "tool_calls": delta["tool_calls"]
                                        }
                            except json.JSONDecodeError:
                                continue
                                
        except asyncio.CancelledError:
            yield {"type": "interrupted"}
        except Exception as e:
            yield {"type": "error", "error": str(e)}
    
    async def stream_anthropic(
        self,
        messages: List[Dict],
        config: Dict,
        tools: List[Dict] = None
    ) -> AsyncIterator[Dict]:
        """
        Stream response from Anthropic API
        
        Args:
            messages: Conversation messages
            config: API configuration
            tools: Optional tool definitions
            
        Yields:
            Dict with chunk data or error
        """
        try:
            from .message_handling import convert_messages_for_anthropic
            
            # Convert messages to Anthropic format
            system_prompt, anthropic_messages = convert_messages_for_anthropic(messages)
            
            request_data = {
                "model": config["model"],
                "max_tokens": 4096,
                "messages": anthropic_messages,
                "stream": True
            }
            
            if system_prompt:
                request_data["system"] = system_prompt
                
            if tools:
                request_data["tools"] = tools
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": config.get("apiKey", ""),
                "anthropic-version": "2023-06-01"
            }
            
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    config["baseURL"] + "/v1/messages",
                    headers=headers,
                    json=request_data,
                    timeout=60.0
                ) as response:
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        yield {"type": "error", "error": f"HTTP {response.status_code}: {error_text.decode()}"}
                        return
                    
                    async for line in response.aiter_lines():
                        if self.interrupted:
                            yield {"type": "interrupted"}
                            return
                            
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                yield {"type": "done"}
                                return
                                
                            try:
                                chunk = json.loads(data)
                                
                                # Handle different event types
                                event_type = chunk.get("type")
                                
                                if event_type == "content_block_delta":
                                    delta = chunk.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        yield {
                                            "type": "content",
                                            "content": delta.get("text", "")
                                        }
                                        
                                elif event_type == "message_stop":
                                    yield {"type": "done"}
                                    return
                                    
                            except json.JSONDecodeError:
                                continue
                                
        except asyncio.CancelledError:
            yield {"type": "interrupted"}
        except Exception as e:
            yield {"type": "error", "error": str(e)}
    
    def interrupt(self):
        """Set interrupt flag to stop streaming"""
        self.interrupted = True
    
    def reset(self):
        """Reset interrupt flag"""
        self.interrupted = False