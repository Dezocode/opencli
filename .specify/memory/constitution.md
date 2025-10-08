# OpenCLI Project Constitution

## Core Values

### 1. Universal Provider Compatibility
- **100% Valid Connection Rate**: Every provider must connect successfully with proper configuration
- **Auto-Configuration**: Provider switching should automatically configure headers, endpoints, and authentication
- **Format Agnostic**: Support all provider-specific message formats and API structures
- **Zero Manual Intervention**: Users should never need to manually adjust configs when switching providers

### 2. Functionality Protection
- **Error Prevention**: Proactive validation to prevent streaming errors and API failures
- **Backward Compatibility**: Never break existing functionality when adding new features
- **Graceful Degradation**: Handle provider-specific quirks without affecting other providers
- **Header Isolation**: Prevent header leakage between different providers

### 3. Provider-Specific Standards

#### Authentication Methods
- **OpenAI/OpenRouter/DeepSeek**: Bearer token in Authorization header
- **Anthropic**: Bearer token + anthropic-version header
- **Google/Gemini**: API key as query parameter (`?key=API_KEY`) OR x-goog-api-key header
- **Auto-Detection**: Automatically detect and apply correct auth method based on provider

#### Message Formats
- **OpenAI-Compatible**: Standard chat completion format
- **Anthropic Messages**: Anthropic-specific message structure
- **Format Mapping**: Automatically translate between formats when switching providers

### 4. Quality Standards

#### Code Quality
- **Type Safety**: Proper typing for all configuration objects
- **Error Handling**: Comprehensive try-catch with meaningful error messages
- **Logging**: Debug logging for provider switches and API calls
- **Documentation**: Clear inline comments explaining provider-specific logic

#### Testing Standards
- **Provider Validation**: Test each provider's auth method and endpoint
- **Switching Tests**: Verify clean transitions between providers
- **Error Scenarios**: Test invalid keys, wrong endpoints, malformed headers
- **Integration Tests**: End-to-end tests for each supported provider

### 5. Development Process

#### Configuration Management
- **Centralized Defaults**: All provider settings in provider_settings.py
- **Runtime Validation**: Validate provider config before creating clients
- **Migration Support**: Auto-migrate legacy configs to new formats
- **User Overrides**: Support custom headers and endpoints per provider

#### Error Handling
- **Informative Messages**: Tell users exactly what's wrong and how to fix it
- **Graceful Failures**: Never crash, always allow continuation
- **Debug Mode**: Detailed logging when enabled
- **Recovery Mechanisms**: Auto-retry with corrected config when possible

### 6. Security Standards

#### API Key Protection
- **Secure Storage**: API keys in .secrets with 0o600 permissions
- **No Logging**: Never log API keys, even in debug mode
- **Memory Safety**: Clear sensitive data after use
- **Query Parameter Safety**: When using query params, ensure proper URL encoding

#### Header Security
- **Clean Isolation**: Reset headers when switching providers
- **No Leakage**: Provider-specific headers never sent to wrong provider
- **Validation**: Reject invalid or dangerous header values

### 7. Performance Requirements

#### Startup Performance
- **Fast Initialization**: Provider config loads < 100ms
- **Lazy Loading**: Only load provider modules when needed
- **Caching**: Cache provider settings after first load

#### Runtime Performance
- **Instant Switching**: Provider switch completes in < 50ms
- **No Blocking**: Client creation doesn't block UI
- **Efficient Headers**: Build headers once, reuse across requests

## Technical Standards

### Architecture Principles
1. **Factory Pattern**: Use factory functions for client creation
2. **Configuration Driven**: All provider behavior controlled by config
3. **Plugin-like**: Easy to add new providers without modifying core
4. **Separation of Concerns**: Auth logic separate from business logic

### File Organization
- `provider_settings.py`: Provider defaults and configuration
- `model_manager.py`: Model discovery and provider detection
- `async_interactive.py`: Runtime client creation and streaming
- `uptime_checker.py`: Provider health monitoring

### Dependencies
- Minimal external dependencies
- Use standard library when possible
- Pin versions for stability
- Document why each dependency exists

## Success Criteria

### Functionality Checklist
- [ ] All providers connect successfully with valid API keys
- [ ] Switching between providers works without errors
- [ ] Each provider uses correct auth method
- [ ] Headers are isolated per provider
- [ ] Message formats are properly translated
- [ ] Debug logging shows provider switches
- [ ] Error messages guide users to solutions
- [ ] Legacy configs auto-migrate

### Quality Checklist
- [ ] Unit tests for each provider's auth method
- [ ] Integration tests for provider switching
- [ ] Error handling tests for all failure modes
- [ ] Performance benchmarks meet targets
- [ ] Documentation covers all providers
- [ ] Code reviewed for security issues

### User Experience Checklist
- [ ] Provider switching is seamless
- [ ] Errors are clear and actionable
- [ ] No manual configuration required
- [ ] Works on first try with valid API keys
- [ ] Debug mode helps troubleshoot issues
