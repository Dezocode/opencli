"""Local Commands"""

async def local_setup(app, session, **context):
    """Local model setup"""
    app.write("[cyan]Local Model Setup[/cyan]\n\n")
    app.write("Checking for Ollama...\n")
