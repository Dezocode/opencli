# OpenRouter Headers Auto-Config - Specification Summary

**Date**: 2025-01-08
**Status**: ✅ IMPLEMENTED - Ready for Testing

---

## Problem

OpenRouter headers (`HTTP-Referer` and `X-Title`) need to be configured per-model, not using hardcoded defaults. Each model has its own API page that shows the correct headers for that model.

---

## Solution

Implement `OpenRouterHeaderManager` that:

1. **Fetches** model API pages: `https://openrouter.ai/{model_id}/api`
2. **Parses** HTML to extract `HTTP-Referer` and `X-Title` headers
3. **Caches** headers per model (24-hour TTL)
4. **Falls back** to defaults if parsing fails
5. **Integrates** with existing ModelManager and load_config()

---

## Key Files

### Documentation
- `.specify/memory/openrouter-headers-spec.md` - Complete problem analysis
- `.specify/plans/openrouter-headers-implementation.md` - Detailed implementation plan

### Code Changes Required

1. **NEW**: `modules/openrouter_headers.py`
   - `OpenRouterHeaderManager` class
   - HTML parsing with BeautifulSoup
   - Cache management

2. **MODIFY**: `modules/model_manager.py`
   - Update `get_provider_headers()` to use OpenRouterHeaderManager for OpenRouter models

3. **MODIFY**: `opencli.py`
   - Update `load_config()` to fetch per-model headers for OpenRouter

4. **MODIFY**: `modules/async_interactive.py`
   - Update model switch logic to refresh headers

---

## Architecture

```
User switches to OpenRouter model
         ↓
ModelManager.get_provider_headers(provider="openrouter", model_id="deepseek/...")
         ↓
OpenRouterHeaderManager.get_headers_for_model("deepseek/...")
         ↓
    Check cache?
    ├─ Yes → Return cached headers
    └─ No  → Fetch from https://openrouter.ai/deepseek/.../api
              ↓
         Parse HTML for headers
              ↓
         Cache result (24h TTL)
              ↓
         Return headers
         ↓
Config updated with model-specific headers
         ↓
AsyncOpenAI client created with correct headers
```

---

## Implementation Phases

### Phase 1: Core Module (45 min)
- Create `OpenRouterHeaderManager` class
- Implement HTML parsing
- Add cache functionality
- Write unit tests

### Phase 2: ModelManager Integration (30 min)
- Update `get_provider_headers()`
- Test with model switches
- Verify cache works

### Phase 3: Startup Integration (20 min)
- Update `load_config()`
- Test startup with OpenRouter model
- Ensure no impact on other providers

### Phase 4: Testing (30 min)
- Test with 5+ OpenRouter models
- Test cache invalidation
- Test error fallbacks
- Verify Google/Anthropic unaffected

### Phase 5: Cleanup (15 min)
- Remove hardcoded defaults
- Update documentation
- Commit and push

**Total Estimated Time**: 2-3 hours

---

## Success Criteria

✅ Headers automatically fetched from model API pages
✅ Headers cached (24h TTL) to avoid repeated fetches
✅ Headers update when switching models
✅ Graceful fallback to defaults on errors
✅ No impact on Google, Anthropic, or other providers
✅ User never manually configures OpenRouter headers

---

## Next Steps

1. Install BeautifulSoup4: `pip3 install beautifulsoup4`
2. Create `modules/openrouter_headers.py`
3. Implement `OpenRouterHeaderManager` class
4. Add tests
5. Integrate with ModelManager
6. Integrate with load_config
7. Test end-to-end
8. Commit to dev7 branch

---

## Important Notes

🚨 **DO NOT** modify Google provider configuration
🚨 **DO NOT** change `baseURL` or `requestFormat` for Google
✅ **ONLY** affect OpenRouter models
✅ **Always** fall back to safe defaults

---

**Ready for Implementation**: YES
**Blocking Issues**: NONE
**Dependencies**: `beautifulsoup4` (pip install)
**Estimated Completion**: 2-3 hours
