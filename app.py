"""
Entry point for Render deployment.
Imports the actual bot from bot/main.py
"""
from bot.main import app

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
