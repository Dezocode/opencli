# OpenCLI SDK

**Complete handler interface and visual flow documentation**

## 📚 Documentation Files

### [VISUAL_FLOW.md](./VISUAL_FLOW.md) - **START HERE**
Complete visual documentation including:
- 📐 Visual layout diagrams
- 🎯 Widget system (MultiLineInput, StatusLine)
- 🔐 Permission buffer flows (commands & tools)
- 📊 Multi-step workflow visualization
- 🔄 Background processing with statusline
- 💾 Permission memory system
- 📋 Handler SDK compliance rules
- 🏗️ Registration templates

### [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
Quick reference card with:
- 🔧 Copy-paste handler template
- 📋 Registration template
- 🎨 Widget state examples
- 🔍 Debug output guide
- ✅ Compliance checking
- 🚀 Testing checklist
- 🎯 Common issues & fixes

## 🔧 SDK Components

### [handler_interface.py](./handler_interface.py)
- `SDKCompliantHandler` - Protocol for all handlers
- `validate_handler()` - Validate handler compliance
- `HandlerCompliance` - Compliance status enum

### [startup_diagnostics.py](./startup_diagnostics.py)
- `StartupDiagnostics` - Validation on startup
- `run_startup_diagnostics()` - Show in permission buffer

## 📋 Handler Requirements

**ALL handlers MUST:**
```python
async def handler_name(app, session, **context):
    """
    ✅ async function
    ✅ Parameters: app, session, **context
    ✅ NO manual buffer management
    ✅ Use app.write() for output
    ✅ Return result value
    """
    pass
```

## 🚀 Quick Start

1. **Read:** [VISUAL_FLOW.md](./VISUAL_FLOW.md) - Understand the complete system
2. **Copy:** Handler template from [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
3. **Register:** Add to `commands/registry.py`
4. **Test:** Run command and check debug output

## 🔍 Files Location

**Project:** `/Users/dezmondhollins/opencli/modules/sdk/`
**Runtime:** `/Users/dezmondhollins/.opencli/modules/sdk/`

Both are now synced!

---

**For visual flow diagrams and complete documentation, see [VISUAL_FLOW.md](./VISUAL_FLOW.md)**
