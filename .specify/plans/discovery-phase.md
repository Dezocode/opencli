# API Key Loading - Discovery Phase
**Date**: 2025-01-08
**Status**: 🔍 ACTIVE INVESTIGATION

---

## Problem Statement

Despite multiple fixes to API key loading logic, the Google provider still fails with:
```
❌ Streaming Error: Error code: 400 - API key not valid. Please pass a valid API key.
```

**Previous fixes that didn't solve it**:
1. ✅ Fixed `get_api_key()` to be provider-aware (loads from models.json)
2. ✅ Fixed Google authentication to use Bearer token (not x-goog-api-key)
3. ✅ Added API key loading to `ModelManager.__init__()`

**Critical question**: Where exactly is the API key being lost between load and actual API call?

---

## Discovery Plan

### Phase 1: Trace API Key Through Complete Flow
**Goal**: Follow the API key from models.json to the actual HTTP request

#### Step 1.1: Verify API Key Storage
- [ ] Read `~/.opencli/models.json` and confirm Google API key exists
- [ ] Verify format: `{"api_keys": {"google": "AIza..."}}`
- [ ] Check key is not corrupted or truncated

#### Step 1.2: Trace opencli.py Startup
- [ ] Read `opencli.py:load_config()` function (lines ~234-350)
- [ ] Trace how `get_api_key(provider)` is called
- [ ] Verify API key is in config dict after load_config()
- [ ] Check if config dict is passed correctly to `run_interactive_async()`

#### Step 1.3: Trace async_interactive.py Entry
- [ ] Read `async_interactive.py:interactive_async()` function
- [ ] Trace how config parameter is received
- [ ] Check if config is modified before first API call
- [ ] Find all places where `create_async_client()` is called

#### Step 1.4: Trace Client Creation
- [ ] Read `create_async_client()` function in async_interactive.py
- [ ] Verify it receives config with apiKey
- [ ] Check AsyncOpenAI instantiation parameters
- [ ] Verify api_key is passed correctly

#### Step 1.5: Trace ModelManager Interaction
- [ ] Read all places where `ModelManager()` is instantiated
- [ ] Check if `config.update(model_mgr.config)` overwrites apiKey
- [ ] Verify `ModelManager.__init__()` loads apiKey correctly
- [ ] Check if there are multiple ModelManager instances

### Phase 2: Identify API Key Loss Points
**Goal**: Find the exact line where apiKey becomes None or empty

#### Step 2.1: Add Strategic Checkpoints
Add minimal, targeted logging at key checkpoints:
- [ ] After `get_api_key()` returns
- [ ] After `load_config()` completes
- [ ] Before `run_interactive_async()` call
- [ ] At start of `interactive_async()`
- [ ] Before each `create_async_client()` call
- [ ] Inside `create_async_client()` before AsyncOpenAI()

#### Step 2.2: Test with Fresh Session
- [ ] Restart OpenCLI with Google provider active
- [ ] Send single test message
- [ ] Capture all checkpoint outputs
- [ ] Identify first checkpoint where apiKey is missing

### Phase 3: Analyze Config Update Pattern
**Goal**: Understand how config mutations affect apiKey

#### Step 3.1: Map All Config Mutations
- [ ] Search for all `config.update()` calls in async_interactive.py
- [ ] Search for all `config[key] = value` assignments
- [ ] Identify which updates might overwrite apiKey
- [ ] Check order of operations

#### Step 3.2: Test ModelManager Config Loading
- [ ] Create standalone test script
- [ ] Instantiate ModelManager with Google provider
- [ ] Check if `model_mgr.config` has apiKey
- [ ] Verify models.json is being read correctly

### Phase 4: Test API Key Propagation
**Goal**: Verify API key actually reaches AsyncOpenAI client

#### Step 4.1: Inspect AsyncOpenAI Client
- [ ] Check AsyncOpenAI client after creation
- [ ] Verify client.api_key property is set
- [ ] Check if client._default_headers includes Authorization
- [ ] Confirm Bearer token format

#### Step 4.2: Test Direct API Call
- [ ] Create minimal test with known-good config
- [ ] Call Google OpenAI endpoint directly
- [ ] Verify same API key works outside OpenCLI
- [ ] Compare request format

---

## Discovery Methodology

### Evidence Collection
1. **Use Grep** to trace function calls and variable assignments
2. **Use Read** to examine complete functions and context
3. **Document findings** in timestamped notes
4. **Create test scripts** to isolate specific behaviors

### Hypothesis Testing
For each potential cause:
1. State the hypothesis
2. Define test to verify/disprove
3. Execute test
4. Document result
5. Update understanding

### Root Cause Criteria
The true root cause must explain:
- ✓ Why API key loads correctly in `get_api_key()`
- ✓ Why test_config_loading.py passes
- ✓ Why actual session startup still fails
- ✓ At what exact point the API key is lost
- ✓ Why ModelManager fix didn't solve it

---

## Potential Root Causes (To Investigate)

### Hypothesis 1: Config Overwrite After Client Creation
**Theory**: Client is created with apiKey, but config.update() overwrites it later
**Test**: Check if client is recreated after config mutations
**Evidence needed**: Timing of create_async_client() calls vs config.update() calls

### Hypothesis 2: Multiple Config Instances
**Theory**: There are multiple config dicts, and API key is in one but not the other
**Test**: Check if opencli.py config is same object as async_interactive.py config
**Evidence needed**: Object IDs and mutation traces

### Hypothesis 3: Client Reuse Without API Key
**Theory**: First client is correct, but subsequent calls reuse a client created without apiKey
**Test**: Trace client lifecycle and reuse pattern
**Evidence needed**: How many times create_async_client() is called per session

### Hypothesis 4: API Key Format Issue
**Theory**: API key has invisible characters or encoding issues
**Test**: Print repr() of API key at each stage
**Evidence needed**: Exact bytes/characters of API key

### Hypothesis 5: Provider Mismatch
**Theory**: Provider switches between config load and API call
**Test**: Log provider value at each checkpoint
**Evidence needed**: Provider consistency throughout flow

### Hypothesis 6: Async Timing Issue
**Theory**: Async operations cause config to be read before apiKey is loaded
**Test**: Check if there are race conditions in config initialization
**Evidence needed**: Timing and order of async operations

---

## Success Criteria

Discovery phase is complete when we can:
1. ✓ Show exact line number where apiKey becomes None/empty
2. ✓ Explain why that line causes the loss
3. ✓ Reproduce the issue in isolated test
4. ✓ Verify fix in isolated test before applying to main code

---

## Next Actions

1. **Execute Phase 1**: Systematic code trace with Grep/Read
2. **Document findings**: Create evidence log with line numbers
3. **Form hypothesis**: Based on evidence, determine most likely cause
4. **Design targeted test**: Create minimal reproduction case
5. **Apply surgical fix**: Fix only the identified root cause

---

**Investigation Start Time**: 2025-01-08T[pending]
**Expected Duration**: 30-60 minutes
**Methodology**: Grep trace → hypothesis → test → fix
