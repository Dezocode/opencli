"""Dev Commands - debug, performance, reload"""

async def debug_toggle(app, session, **context):
    """Toggle debug mode"""
    session.debug_mode = not session.debug_mode
    status = "enabled" if session.debug_mode else "disabled"
    color = "green" if session.debug_mode else "yellow"
    app.write(f"[{color}]Debug mode {status}[/{color}]\n\n")

async def performance_monitor(app, session, **context):
    """Performance monitoring controls"""
    app.write("[cyan]Performance Monitoring[/cyan]\n\n")
    app.write("Coming soon: Real-time performance metrics\n")

async def reload_modules(app, session, **context):
    """Hot-reload modules"""
    import sys
    import importlib
    
    app.write("[cyan]Reloading modules...[/cyan]\n\n")
    
    # Clear module cache
    modules_to_reload = [k for k in sys.modules.keys() if 'modules.' in k]
    for mod in modules_to_reload:
        if mod in sys.modules:
            del sys.modules[mod]
    
    app.write(f"[green]✓ Cleared {len(modules_to_reload)} cached modules[/green]\n\n")
