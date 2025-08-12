import asyncio
import logging
import re
from neonize.aioze.client import NewAClient
from neonize.aioze.events import MessageEv, ConnectedEv
from .plugin_manager import PluginManager
from .py_handler import handle_message
from colored import fg, attr
import pyfiglet

def print_banner():
    """Prints a cool startup banner."""
    color = fg('yellow')
    reset = attr('reset')
    author_color = fg('cyan')

    # Generate ASCII art
    ascii_art = pyfiglet.figlet_format("MaycolAIUltraMD", font="block")

    # Print banner
    print(f"{color}{ascii_art}{reset}")
    print(f"{author_color}                 Hecho por Maycol                           {reset}")
    print()

def setup_logging():
    """Sets up the colored logging."""
    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'WARNING': fg('yellow'),
            'INFO': fg('green'),
            'DEBUG': fg('blue'),
            'CRITICAL': fg('red'),
            'ERROR': fg('red')
        }

        def format(self, record):
            log_message = super().format(record)
            color = self.COLORS.get(record.levelname)
            if color:
                return f"{color}{log_message}{attr('reset')}"
            return log_message

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter('%(levelname)s: %(message)s'))
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)

async def main():
    """Main function to initialize, configure, and run the bot."""
    print_banner()
    setup_logging()

    # --- Interactive Login ---
    print("Please choose a login method:")
    print(f"{fg('green')}1. Scan QR Code{attr('reset')}")
    print(f"{fg('cyan')}2. Use Pairing Code (Phone Number){attr('reset')}")

    choice = ""
    while choice not in ['1', '2']:
        choice = await asyncio.to_thread(input, "> ")

    client: NewAClient

    if choice == '1':
        # Assume 'print_qr_in_terminal' is a valid, but perhaps non-existent, kwarg.
        # The library might print QR by default if not logged in.
        try:
            client = NewAClient("maycol_ai_bot_session.db", print_qr_in_terminal=True)
        except TypeError:
            logging.warning("`print_qr_in_terminal` is not a valid argument for NewAClient. "
                            "Relying on default behavior to print QR code.")
            client = NewAClient("maycol_ai_bot_session.db")

    elif choice == '2':
        client = NewAClient("maycol_ai_bot_session.db")

        phone_number = ""
        while not re.match(r'^\d{10,15}$', phone_number):
             phone_number = await asyncio.to_thread(
                input,
                f"{fg('yellow')}Please enter your full phone number without '+' or spaces (e.g., 15551234567):{attr('reset')} "
             )

        logging.info(f"Requesting pairing code for {phone_number}...")
        try:
            # Assume this method exists and returns the code.
            pairing_code = await client.request_pairing_code(phone_number)
            logging.info(f"{fg('magenta')}--- PAIRING CODE ---{attr('reset')}")
            logging.info(f"Your pairing code is: {fg('cyan')}{pairing_code}{attr('reset')}")
            logging.info(f"{fg('magenta')}--------------------{attr('reset')}")
        except AttributeError:
            logging.error("`request_pairing_code` method not found on the client.")
            logging.error("Cannot proceed with pairing code login.")
            return
        except Exception as e:
            logging.error(f"Failed to get pairing code: {e}")
            return

    plugin_manager = PluginManager()

    # Define event handlers
    @client.event
    async def on_connected(_: NewAClient, event: ConnectedEv):
        """Handles the 'connected' event."""
        logging.info("🎉 Bot connected successfully!")
        logging.info(f"Connected to account: {event.device}")

    @client.event
    async def on_message(client: NewAClient, event: MessageEv):
        """Handles incoming messages by delegating to the handler."""
        await handle_message(client, event, plugin_manager)

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
