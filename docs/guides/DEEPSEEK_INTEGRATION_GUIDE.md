# DeepSeek Chat v3.1 Integration Guide

## Overview

This guide explains how to integrate and use DeepSeek Chat v3.1 with the OpenCLI architecture. DeepSeek Chat v3.1 is a powerful language model that can be used as an alternative or complement to Claude models.

## Supported DeepSeek Models

```yaml
# Available in providers.yaml
deepseek-chat-v3.1:
  name: "DeepSeek Chat v3.1"
  context_window: 131072
  max_tokens: 4096
  pricing:
    input: 0.14
    output: 0.28
  capabilities:
    - code
    - reasoning
    - long_context
    - multilingual
```

## Configuration Setup

### 1. Add DeepSeek Provider

Edit `providers.yaml` to include DeepSeek:

```yaml
providers:
  deepseek:
    base_url: "https://api.deepseek.com/v1"
    models:
      - deepseek-chat-v3.1
      - deepseek-coder-v2
```

### 2. Set API Key

Add your DeepSeek API key to `.secrets`:

```bash
echo "DEEPSEEK_API_KEY=your_api_key_here" >> ~/.opencli/.secrets
chmod 600 ~/.opencli/.secrets
```

### 3. Configure Default Model

Edit `config.json`:

```json
{
  "default_model": "deepseek-chat-v3.1",
  "fallback_models": ["claude-3.5-sonnet", "gpt-4o"],
  "providers": {
    "deepseek": {
      "priority": 1,
      "timeout": 30
    }
  }
}
```

## Architecture Integration

### Agent Configuration

Create a DeepSeek-specific agent in `agents/configs/deepseek.yaml`:

```yaml
name: "deepseek-coder"
description: "DeepSeek Chat v3.1 optimized for coding tasks"
model: "deepseek-chat-v3.1"
system_prompt: |
  You are DeepSeek Chat v3.1, a coding-focused AI assistant. You excel at:
  - Code generation and optimization
  - Algorithm design and analysis
  - Debugging complex systems
  - Multilingual programming support
  - Long context code understanding
  
  Always provide efficient, production-ready code with explanations.

capabilities:
  - code_generation
  - code_review
  - debugging
  - optimization
  - documentation

parameters:
  temperature: 0.1
  top_p: 0.9
  max_tokens: 4096
```

### Context Building for DeepSeek

DeepSeek Chat v3.1 supports 131K context window. Update context builder:

```python
# In context_builder.py

def build_deepseek_context(agent_config, project_context):
    """Build optimized context for DeepSeek models"""
    context_parts = []
    
    # System prompt
    context_parts.append(agent_config.get('system_prompt', ''))
    
    # Project context (AGENTS.md + current state)
    if project_context:
        context_parts.append("\n=== PROJECT CONTEXT ===")
        context_parts.append(project_context)
    
    # Tool definitions
    context_parts.append("\n=== AVAILABLE TOOLS ===")
    context_parts.append(load_tool_descriptions())
    
    return "\n".join(context_parts)
```

## Usage Patterns

### 1. Direct Model Selection

```bash
# Use DeepSeek explicitly
opencli --model deepseek-chat-v3.1 "Write a Python API server"

# Or set as default in session
opencli --set-model deepseek-chat-v3.1
```

### 2. Agent-Based Usage

```bash
# Use DeepSeek coding agent
opencli --agent deepseek-coder "Optimize this algorithm:"

# Switch between agents
opencli --agent claude-reviewer --then deepseek-coder "Review then optimize"
```

### 3. Long Context Processing

DeepSeek excels with large codebases:

```bash
# Process entire project
opencli --model deepseek-chat-v3.1 --context . "Analyze this codebase"

# With file attachments
opencli --model deepseek-chat-v3.1 --file large_project.zip "Review architecture"
```

## Performance Optimization

### 1. Token Usage

DeepSeek pricing:
- Input: $0.14 per 1M tokens
- Output: $0.28 per 1M tokens

Optimize with:
```python
# Use concise context building
context = build_minimal_context(agent, current_task)

# Enable streaming to reduce latency
response = await deepseek_client.chat.completions.create(
    model="deepseek-chat-v3.1",
    messages=messages,
    stream=True,
    max_tokens=2048  # Conservative output
)
```

### 2. Rate Limiting

Configure in `config.json`:

```json
{
  "providers": {
    "deepseek": {
      "rate_limit": {
        "requests_per_minute": 60,
        "tokens_per_minute": 100000
      },
      "retry": {
        "max_attempts": 3,
        "backoff_factor": 2
      }
    }
  }
}
```

### 3. Fallback Strategy

```python
def get_best_model(task_type, context_length):
    """Choose optimal model based on task"""
    if context_length > 100000:
        return "deepseek-chat-v3.1"  # Best for long context
    elif task_type == "coding":
        return "deepseek-chat-v3.1"  # Excellent for code
    elif task_type == "reasoning":
        return "claude-3.5-sonnet"   # Strong reasoning
    else:
        return "gpt-4o"             # General purpose
```

## Advanced Features

### 1. Multi-Model Collaboration

```yaml
# agents/configs/collaborative.yaml
name: "code-review-team"
description: "Multi-model code review workflow"
workflow:
  - agent: "deepseek-coder"
    task: "Generate initial implementation"
  - agent: "claude-reviewer"
    task: "Review code quality and security"
  - agent: "gpt-4o-doc"
    task: "Generate documentation"
```

### 2. Context-Aware Model Switching

```python
def adaptive_model_switching(current_context, next_task):
    """Switch models based on context and task"""
    context_size = len(current_context)
    
    if context_size > 80000:
        # DeepSeek for very long context
        return "deepseek-chat-v3.1"
    elif next_task.startswith("code") or next_task.startswith("implement"):
        # DeepSeek for coding tasks
        return "deepseek-chat-v3.1"
    elif "review" in next_task or "analyze" in next_task:
        # Claude for analysis
        return "claude-3.5-sonnet"
    else:
        # GPT-4 for general tasks
        return "gpt-4o"
```

### 3. Cost Optimization

```python
def cost_aware_model_selection(task, budget):
    """Choose model based on cost constraints"""
    models = {
        "deepseek-chat-v3.1": {"input": 0.14, "output": 0.28},
        "claude-3.5-sonnet": {"input": 3.00, "output": 15.00},
        "gpt-4o": {"input": 5.00, "output": 15.00}
    }
    
    # Estimate token usage
    estimated_tokens = estimate_token_usage(task)
    
    # Find most cost-effective model within budget
    affordable_models = [
        (model, cost) for model, cost in models.items()
        if (cost["input"] + cost["output"]) * estimated_tokens / 1000000 <= budget
    ]
    
    return min(affordable_models, key=lambda x: x[1])[0] if affordable_models else "deepseek-chat-v3.1"
```

## Troubleshooting

### Common Issues

1. **API Timeouts**: Increase timeout in config
2. **Rate Limiting**: Implement retry logic with backoff
3. **Context Truncation**: Use DeepSeek for very long contexts
4. **Cost Overruns**: Set usage limits and monitor spending

### Debug Commands

```bash
# Check DeepSeek connectivity
opencli --test-provider deepseek

# Monitor token usage
opencli --stats --model deepseek-chat-v3.1

# Reset context cache
opencli --clear-cache
```

## Best Practices

1. **Use DeepSeek for**:
   - Large codebase analysis
   - Coding tasks
   - Long document processing
   - Cost-sensitive applications

2. **Use Claude/GPT for**:
   - Complex reasoning
   - Creative writing
   - Precise instruction following
   - Multi-step planning

3. **Always**:
   - Monitor token usage
   - Set budget limits
   - Use appropriate context windows
   - Implement fallback strategies

## Performance Benchmarks

| Task Type | DeepSeek v3.1 | Claude 3.5 | GPT-4o |
|-----------|---------------|------------|--------|
| Code Generation | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Long Context | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Cost Efficiency | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| Reasoning | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Creativity | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## Conclusion

DeepSeek Chat v3.1 is an excellent choice for:
- Cost-effective AI assistance
- Large context window applications
- Coding-focused tasks
- Budget-conscious projects

Integrate it into your OpenCLI workflow using the patterns described above for optimal performance and cost efficiency.