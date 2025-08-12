import asyncio
import logging
from neonize.aioze.client import NewAClient
from neonize.aioze.events import MessageEv, ConnectedEv
from .plugin_manager import PluginManager
from .py_handler import handle_message

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize client and plugin manager
# Session file will be created inside the python_bot directory
client = NewAClient("maycol_ai_bot_session.db")
plugin_manager = PluginManager()

@client.event
async def on_connected(_: NewAClient, event: ConnectedEv):
    """Handles the 'connected' event."""
    logging.info("🎉 Bot connected successfully!")
    logging.info(f"Connected to account: {event.device}")

@client.event
async def on_message(client: NewAClient, event: MessageEv):
    """Handles incoming messages by delegating to the handler."""
    await handle_message(client, event, plugin_manager)

async def main():
    """Main function to connect the client and load plugins."""
    # Load plugins and start watching
    plugin_manager.load_all_plugins()
    plugin_manager.watch_plugins()

    logging.info("Connecting to WhatsApp...")
    await client.connect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped manually.")
